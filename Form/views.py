from django.shortcuts import render

import json
import pydoc
import re
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login ,logout,get_user_model
from Account.forms import RegistrationForm
from Account.models import *
from Masters.models import *
import Db 
import bcrypt
from django.contrib.auth.decorators import login_required
from TDMS.encryption import *
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from Account.utils import decrypt_email, encrypt_email
import requests
import traceback
import pandas as pd
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages
import openpyxl
from openpyxl.styles import Font, Border, Side
import calendar
from datetime import datetime, timedelta
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
from Account.models import *
from Masters.models import *
from Form.models import *
from Account.db_utils import callproc
from django.views.decorators.csrf import csrf_exempt
import os
from django.urls import reverse
from TDMS.settings import *
import logging
from django.http import FileResponse, Http404
import mimetypes

from Workflow.models import workflow_action_master


# Create your views here.
def format_label_name(parameter_name):
    """Convert parameter name to a proper label format."""
    return " ".join(re.findall(r'[A-Za-z]+', parameter_name)).title()


def form_builder(request):
    form_id = request.GET.get('form_id')
    common_options = list(CommonMaster.objects.filter(type='attribute').values("id", "control_value"))
    sub_control = list(ValidationMaster.objects.values("id", "control_name", "control_value", "field_type","datatype"))
    regex = list(RegexPattern.objects.values("id", "input_type", "regex_pattern", "description"))  
    dropdown_options = list(ControlParameterMaster.objects.values("control_name", "control_value"))

    if not form_id:  
        return render(request, "Form/form_builder.html", {
            "regex":json.dumps(regex),
            "dropdown_options": json.dumps(dropdown_options),
            "common_options": json.dumps(common_options),
            "sub_control": json.dumps(sub_control)
        })

    try:
        form_id = dec(form_id)  # Decrypt form_id
        form = get_object_or_404(Form, id=form_id)  # Get form or return 404
        fields = FormField.objects.filter(form_id=form_id)
        validations = FieldValidation.objects.filter(form_id=form_id)
    except Exception as e:
        print(f"Error fetching form data: {e}")  # Debugging
        return render(request, "Form/form_builder.html", {
            "regex":json.dumps(regex),
            "dropdown_options": json.dumps(dropdown_options),
            "common_options": json.dumps(common_options),
            "sub_control": json.dumps(sub_control),
            "error": "Invalid form ID"
        })

    # Organizing validations in a dictionary {field_id: [{validation_type, validation_value}]}
    validation_dict = {}

    for validation in validations:
        field_id = validation.field.id

        if field_id not in validation_dict:
            validation_dict[field_id] = []

        validation_dict[field_id].append({
            "validation_type": validation.sub_master.control_value,  # Assuming 'control_value' holds validation type
            "validation_value": validation.value
        })

    # Convert fields and their validation rules to JSON
    form_fields_json = json.dumps([
        {
            "id": field.id,
            "label": field.label,
            "type": field.field_type,
            "options": field.values.split(",") if field.values else [],
            "attributes": field.attributes,
            "validation": validation_dict.get(field.id, [])  # Attach validation rules
        }
        for field in fields
    ])

    return render(request, "Form/form_builder.html", {
        "form": form,
        "regex":json.dumps(regex),
        "form_fields_json": form_fields_json,
        "dropdown_options": json.dumps(dropdown_options),
        "common_options": json.dumps(common_options),
        "sub_control": json.dumps(sub_control)
    })

def format_label(label):
    """Format label to have proper capitalization."""
    words = re.split(r'[_ ]+', label.strip())
    return ' '.join(word.capitalize() for word in words)



@csrf_exempt
def save_form(request):
    user  = request.session.get('user_id', '')
    try:
        if request.method == "POST":
            form_name = request.POST.get("form_name")
            form_description = request.POST.get("form_description")
            form_data_json = request.POST.get("form_data")

            if not form_data_json:
                return JsonResponse({"error": "No form data received"}, status=400)

            try:
                form_data = json.loads(form_data_json)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON data"}, status=400)

            
            form = Form.objects.create(name=form_name, description=form_description)

            for field in form_data:
                # Create the form field entry
                form_field = FormField.objects.create(
                    form=form,
                    label=field.get("label", ""),
                    field_type=field.get("type", ""),
                    attributes=field.get("attributes", ""),
                    values=",".join(option.strip() for option in field.get("options", [])),
                )
                field_id = form_field.id

               
                # Handle regex & max_length validation separately
                if "validation" in field and isinstance(field["validation"], list):
                    for validation_item in field["validation"]:
                        validation_type = validation_item.get("validation_type")
                        validation_value = validation_item.get("validation_value", "")
                        sub_master_id = validation_item.get("id")  # Get sub_master_id for regex

                        if validation_type and validation_value and sub_master_id:
                            FieldValidation.objects.create(
                                field=get_object_or_404(FormField, id=field_id),
                                form=get_object_or_404(Form, id=form.id),
                                sub_master_id=sub_master_id,  # Save regex/max_length master ID
                                value=validation_value,  # Save regex pattern or max_length
                            )


                # ✅ Save `file` validation (New Logic)
                if field.get("type") == "file" and "validation" in field:
                    file_validation_list = field["validation"]  # This is a list

                    if file_validation_list and isinstance(file_validation_list, list):
                        file_validation = file_validation_list[0]  # Get first item (dictionary)

                        file_validation_value = file_validation.get("validation_value", "")  # Extract ".jpg, .jpeg, .png"
                        sub_master_id = file_validation.get("id", None)  # Extract "2"

                        # Create FieldValidation record
                        FieldValidation.objects.create(
                            field=get_object_or_404(FormField, id=field_id),
                            form=get_object_or_404(Form, id=form.id),
                            sub_master_id=sub_master_id,  # Save only the ID
                            value=file_validation_value,  # Save only ".jpg, .jpeg, .png"
                        )


            messages.success(request, "Form and fields saved successfully!!")
            new_url = f'/masters?entity=form&type=i'
            return redirect(new_url) 

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        callproc("stp_error_log", [fun, str(e), user])
        messages.error(request, 'Oops...! Something went wrong!')
        return JsonResponse({"error": "Something went wrong!"}, status=500)

    finally:
        Db.closeConnection()



@csrf_exempt
def update_form(request, form_id):
    try:
        if request.method == "POST":
            form_name = request.POST.get("form_name")
            form_description = request.POST.get("form_description")
            form_data_json = request.POST.get("form_data")

            if not form_data_json:
                return JsonResponse({"error": "No form data received"}, status=400)

            try:
                form_data = json.loads(form_data_json)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON data"}, status=400)

            # Update form details
            form = get_object_or_404(Form, id=form_id)
            form.name = form_name
            form.description = form_description
            form.save()

            # Delete existing form fields and validations
            FormField.objects.filter(form=form).delete()
            FieldValidation.objects.filter(form=form).delete()

            for field in form_data:
                # ✅ Ensure attributes are stored correctly
                attributes_value = field.get("attributes", "")

                form_field = FormField.objects.create(
                    form=form,
                    label=field.get("label", ""),
                    field_type=field.get("type", ""),
                    attributes=attributes_value,  # ✅ Fixed attribute storage
                    values=",".join(option.strip() for option in field.get("options", [])),
                )

                field_id = form_field.id

                # ✅ Ensure 'subValues' exists
                if "validation" in field and isinstance(field["validation"], list):
                    for validation_item in field["validation"]:
                        validation_type = validation_item.get("validation_type")
                        validation_value = validation_item.get("validation_value", "")
                        sub_master_id = validation_item.get("id")  # Get sub_master_id for regex

                        if validation_type and validation_value and sub_master_id:
                            FieldValidation.objects.create(
                                field=get_object_or_404(FormField, id=field_id),
                                form=get_object_or_404(Form, id=form.id),
                                sub_master_id=sub_master_id,  # Save regex/max_length master ID
                                value=validation_value,  # Save regex pattern or max_length
                            )
                if field.get("type") == "file" and "validation" in field:
                    file_validation_list = field["validation"]  # This is a list

                    if file_validation_list and isinstance(file_validation_list, list):
                        file_validation = file_validation_list[0]  # Get first item (dictionary)

                        file_validation_value = file_validation.get("validation_value", "")  # Extract ".jpg, .jpeg, .png"
                        sub_master_id = file_validation.get("id", None)  # Extract "2"

                        # Create FieldValidation record
                        FieldValidation.objects.create(
                            field=get_object_or_404(FormField, id=field_id),
                            form=get_object_or_404(Form, id=form.id),
                            sub_master_id=sub_master_id,  # Save only the ID
                            value=file_validation_value,  # Save only ".jpg, .jpeg, .png"
                        )

            messages.success(request, "Form updated successfully!!")
            return redirect('/masters?entity=form&type=i')
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        callproc("stp_error_log", [fun, str(e), request.user])
        messages.error(request, "Oops...! Something went wrong!")
        return JsonResponse({"error": "Something went wrong!"}, status=500)
    finally:
        Db.closeConnection()

def form_action_builder(request):
    action_id = request.GET.get('action_id')
    master_values = FormAction.objects.filter(is_master = 1).all()
    button_type = list(CommonMaster.objects.filter(type='button').values("id", "control_value"))
    dropdown_options = list(ControlParameterMaster.objects.filter(is_action=1).values("control_name", "control_value"))

    if not action_id:  
        return render(request,  "Form/form_action_builder.html", {
            "master_values":master_values,
            "button_type":json.dumps(button_type),
            "dropdown_options": json.dumps(dropdown_options),
        })

    try:
        action_id = dec(action_id)  # Decrypt form_id
        form = get_object_or_404(FormAction, id=action_id)  # Get form or return 404
        fields = FormActionField.objects.filter(action_id=action_id)
    except Exception as e:
        print(f"Error fetching form data: {e}")  # Debugging
        return render(request, "Form/form_action_builder.html", {\
            "dropdown_options": json.dumps(dropdown_options),
            "error": "Invalid form ID"
        })

    form_fields_json = json.dumps([
        {
            "id": field.id,
            "label": field.label_name,
            "bg_color":field.bg_color,
            "text_color":field.text_color,
            "type": field.type,
            "options": field.dropdown_values.split(",") if field.dropdown_values else [],
            "button_type":field.button_type,
            "status":field.status,
            "value":field.button_name
        }
        for field in fields
    ])

    return render(request, "Form/form_action_builder.html", {
        "form": form,
        "master_values":master_values,
        "button_type":json.dumps(button_type),
        "form_fields_json": form_fields_json,
        "dropdown_options": json.dumps(dropdown_options),
    })



@csrf_exempt
def save_form_action(request):
    user  = request.session.get('user_id', '')
    try:

        if request.method == "POST":
            form_name = request.POST.get("action_name")
            form_master = 1 if request.POST.get("is_master") == "on" else 0
            form_data_json = request.POST.get("form_data")

            if not form_data_json:
                return JsonResponse({"error": "No form data received"}, status=400)

            try:
                form_data = json.loads(form_data_json)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON data"}, status=400)

            
            form_action = FormAction.objects.create(name=form_name,is_master= form_master)


            for field in form_data:
                field_type = field.get("type", "")
                
                if field_type == "button":
                    label_name = None
                    dropdown_values = None
                    bg_color = field.get("bg_color", "")
                    text_color = field.get("text_color", "")
                    status = field.get("status",None)
                    button_name = field.get("value", "")
                else:
                    label_name = field.get("label", "")
                    button_name= None
                    bg_color = None
                    text_color = None
                    status = None
                    

                # Create the form field entry
                FormActionField.objects.create(
                    action=form_action,
                    type=field_type,
                    label_name=label_name,
                    button_name= button_name,
                    bg_color=bg_color,
                    text_color=text_color,
                    button_type=field.get("buttonType", ""),
                    status=status,
                    dropdown_values=",".join(option.strip() for option in field.get("options", []))
                )

            messages.success(request, "Form Action and fields saved successfully!!")
            new_url = f'/masters?entity=action&type=i'
            return redirect(new_url) 

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        callproc("stp_error_log", [fun, str(e), user])
        messages.error(request, 'Oops...! Something went wrong!')
        return JsonResponse({"error": "Something went wrong!"}, status=500)

    finally:
        Db.closeConnection()

@csrf_exempt
def update_action_form(request, form_id):
    user  = request.session.get('user_id', '')
    try:  # Decoding action_id if necessary

        if request.method == "POST":
            # Getting form data from POST request
            form_name = request.POST.get("action_name")
            form_master = 1 if request.POST.get("is_master") == "on" else 0
            form_data_json = request.POST.get("form_data")

            if not form_data_json:
                return JsonResponse({"error": "No form data received"}, status=400)

            try:
                form_data = json.loads(form_data_json)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON data"}, status=400)

            # Update the FormAction instance
            form_action = FormAction.objects.filter(id=form_id).first() if form_id else None
            if not form_action:
                return JsonResponse({"error": "Form action not found"}, status=404)

            form_action.name = form_name
            form_action.is_master = form_master
            form_action.save()

            # Delete existing form fields for this action
            FormActionField.objects.filter(action_id=form_id).delete()

            # Insert the new form fields
            for field in form_data:
                field_type = field.get("type", "").strip()

                if field_type == "button":
                    label_name = None
                    bg_color = field.get("bg_color", "")
                    text_color = field.get("text_color", "")
                    status = field.get("status", None).strip() if field.get("status") else None
                    button_name = field.get("value", "").strip()
                else:
                    label_name = field.get("label", "").strip()
                    button_name = None
                    bg_color = None
                    text_color = None
                    status = None

                # Create the form field entry
                FormActionField.objects.create(
                    action=form_action,
                    type=field_type,
                    label_name=label_name,
                    button_name=button_name,
                    bg_color=bg_color,
                    text_color=text_color,
                    button_type=field.get("buttonType", ""),
                    status=status,
                    dropdown_values=",".join(option.strip() for option in field.get("options", []))
                )

            messages.success(request, "Form Action and fields Updated successfully!!")
            new_url = f'/masters?entity=action&type=i'
            return redirect(new_url)

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        # Log error in the database
        callproc("stp_error_log", [fun, str(e), user])
        messages.error(request, 'Oops...! Something went wrong!')
        return JsonResponse({"error": "Something went wrong!"}, status=500)

    finally:
        Db.closeConnection()





def form_master(request):
    try:
        if request.method == "POST":
            form_id = request.POST.get("form")
            
            fields = FormField.objects.filter(form_id=form_id).values("id", "label", "field_type", "values", "attributes","form_id","form_id__name")
            fields = list(fields)
            
            for field in fields:
                # Convert "values" from comma-separated string to list
                field["values"] = field["values"].split(",") if field["values"] else []
                
                # Convert "attributes" from comma-separated string to list
                attributes_list = field["attributes"].split(",") if field["attributes"] else []
                field["required"] = "required" if "1" in attributes_list else ""
                field["disabled"] = "disabled" if "3" in attributes_list else ""
                field["readonly"] = "readonly" if "4" in attributes_list else ""
                
                # Fetch field validation rules
                validations = FieldValidation.objects.filter(field_id=field["id"], form_id=form_id).values("value")
                field["validations"] = list(validations)
                
                # Extract file format for file fields
                if field["field_type"] == "file":
                    file_validation = next((v for v in field["validations"]), None)
                    field["accept"] = file_validation["value"] if file_validation else ""

                if field["field_type"] == "text":
                    file_validation = next((v for v in field["validations"]), None)
                    field["accept"] = file_validation["value"] if file_validation else ""
            
            return render(request, "Form/_formfields.html", {"fields": fields})
        
        else:
            form_data_id = request.GET.get("form")

            if form_data_id:
                form_data_id = dec(form_data_id)
                form_instance = FormData.objects.filter(id=form_data_id).values("id","form_id").first()
                if form_instance:
                    form_id = form_instance["form_id"]
                    fields = FormField.objects.filter(form_id=form_id).values(
                        "id", "label", "field_type", "values", "attributes", "form_id", "form_id__name"
                    )
                    fields = list(fields)


                # Fetch saved values for the form data
                field_values = FormFieldValues.objects.filter(form_data_id=form_data_id).values("field_id", "value")

                # Convert to a dictionary for quick lookup
                values_dict = {fv["field_id"]: fv["value"] for fv in field_values}

                for field in fields:
                    field["values"] = field["values"].split(",") if field["values"] else []
                    
                    attributes_list = field["attributes"].split(",") if field["attributes"] else []
                    field["required"] = "required" if "1" in attributes_list else ""
                    field["disabled"] = "disabled" if "3" in attributes_list else ""
                    field["readonly"] = "readonly" if "4" in attributes_list else ""

                    # Fetch validation rules
                    validations = FieldValidation.objects.filter(field_id=field["id"], form_id=form_id).values("value")
                    field["validations"] = list(validations)

                    # Extract file format for file fields
                    if field["field_type"] == "file":
                        file_validation = next((v for v in field["validations"]), None)
                        field["accept"] = file_validation["value"] if file_validation else ""

                    # Set existing values if available
                    field["value"] = values_dict.get(field["id"], "")

                return render(request, "Form/_formfieldedit.html", {"fields": fields,"type":"edit","form_data_id":form_data_id})
            else:
                type = request.GET.get("type")
                form = Form.objects.all()
                return render(request, "Form/form_master.html", {"form": form,"type":type})
    
    except Exception as e:
        traceback.print_exc()
        messages.error(request, 'Oops...! Something went wrong!')
        return JsonResponse({"error": "Something went wrong!"}, status=500)
    

def common_form_post(request):
    try:
        if request.method != "POST":
            return JsonResponse({"error": "Invalid request method"}, status=400)

        created_by = request.session.get('user_id', '').strip()
        form_name = request.POST.get('form_name', '').strip()

        # Get form ID
        form_id_key = next((key for key in request.POST if key.startswith("form_id_")), None)
        if not form_id_key:
            return JsonResponse({"error": "Form ID not found"}, status=400)

        form_id = request.POST.get(form_id_key, '').strip()
        form = get_object_or_404(Form, id=form_id)

        # Create FormData entry
        form_data = FormData.objects.create(form=form)
        form_data.req_no = f"REQNO-00{form_data.id}"
        form_data.save()

        saved_values = []
        file_records = []
        field_value_map = {}  # Map to store field_id -> FormFieldValues instance

        # Process each field
        for key, value in request.POST.items():
            if key.startswith("field_id_"):
                field_id = value.strip()
                field = get_object_or_404(FormField, id=field_id)

                # Get actual input value
                input_value = request.POST.get(f"field_{field_id}", "").strip()

                # Insert into FormFieldValues first
                form_field_value = FormFieldValues.objects.create(
                    form_data=form_data,form=form, field=field, value=input_value, created_by=created_by
                )
                field_value_map[field_id] = form_field_value

        # Handle file uploads
        for field_key, uploaded_file in request.FILES.items():
            if field_key.startswith("field_"):
                field_id = field_key.split("_")[-1].strip()
                field = get_object_or_404(FormField, id=field_id)

                # Retrieve the corresponding FormFieldValues instance
                form_field_value = field_value_map.get(field_id)
                if not form_field_value:
                    continue

                # Define file directory
                file_dir = os.path.join(settings.MEDIA_ROOT, form_name, created_by, form_data.req_no)
                os.makedirs(file_dir, exist_ok=True)

                # Generate filename
                original_file_name, file_extension = os.path.splitext(uploaded_file.name.strip())
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                saved_file_name = f"{original_file_name}_{timestamp}{file_extension}"

                # Save file
                fs = FileSystemStorage(location=file_dir)
                saved_path = fs.save(saved_file_name, uploaded_file)

                # Generate file path
                file_path = os.path.join(form_name, created_by, form_data.req_no, saved_file_name)

                # Insert into FormFile
                form_file = FormFile.objects.create(
                    file_name=saved_file_name,
                    uploaded_name=uploaded_file.name.strip(),
                    file_id=form_field_value.id,  # Link with FormFieldValues
                    file_path=file_path,
                    form_data=form_data,
                    form=form,
                    field=field
                )

                # Update FormFieldValues with FormFile ID
                form_field_value.value = str(form_file.id)
                form_field_value.save()

        messages.success(request, "Form data saved successfully!")

    except Exception as e:
        traceback.print_exc()
        messages.error(request, 'Oops...! Something went wrong!')

    finally:
        return redirect('/masters?entity=form_master&type=i')


def common_form_edit(request):
    try:
        if request.method != "POST":
            return JsonResponse({"error": "Invalid request method"}, status=400)

        form_data_id = request.POST.get("form_data_id")

        if not form_data_id:
            return JsonResponse({"error": "form_data_id is required"}, status=400)

        form_data = get_object_or_404(FormData, id=form_data_id)

        # Update form_id if provided
        form_id_key = next((key for key in request.POST if key.startswith("form_id_")), None)
        if form_id_key:
            form_id = request.POST.get(form_id_key, "").strip()
            form_data.form_id = form_id
            form_data.save()

        # Delete existing records in related tables
        FormFile.objects.filter(form_data_id=form_data_id).delete()
        FormFieldValues.objects.filter(form_data_id=form_data_id).delete()

        created_by = request.session.get("user_id", "").strip()
        form_name = request.POST.get("form_name", "").strip()

        saved_values = []
        file_records = []
        field_value_map = {}

        # Process each field
        for key, value in request.POST.items():
            if key.startswith("field_id_"):
                field_id = value.strip()
                field = get_object_or_404(FormField, id=field_id)

                # Get actual input value
                input_value = request.POST.get(f"field_{field_id}", "").strip()

                # Insert into FormFieldValues
                form_field_value = FormFieldValues.objects.create(
                    form_data=form_data, field=field, value=input_value, created_by=created_by
                )
                field_value_map[field_id] = form_field_value

        # Handle file uploads
        for field_key, uploaded_file in request.FILES.items():
            if field_key.startswith("field_"):
                field_id = field_key.split("_")[-1].strip()
                field = get_object_or_404(FormField, id=field_id)

                # Retrieve the corresponding FormFieldValues instance
                form_field_value = field_value_map.get(field_id)
                if not form_field_value:
                    continue

                # Define file directory
                file_dir = os.path.join(settings.MEDIA_ROOT, form_name, created_by, form_data.req_no)
                os.makedirs(file_dir, exist_ok=True)

                # Generate filename
                original_file_name, file_extension = os.path.splitext(uploaded_file.name.strip())
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                saved_file_name = f"{original_file_name}_{timestamp}{file_extension}"

                # Save file
                fs = FileSystemStorage(location=file_dir)
                saved_path = fs.save(saved_file_name, uploaded_file)

                # Generate file path
                file_path = os.path.join(form_name, created_by, form_data.req_no, saved_file_name)

                # Insert into FormFile
                form_file = FormFile.objects.create(
                    file_name=saved_file_name,
                    uploaded_name=uploaded_file.name.strip(),
                    file_id=form_field_value.id,  # Link with FormFieldValues
                    file_path=file_path,
                    form_data=form_data,
                    form=form_data.form,
                    field=field
                )

                # Update FormFieldValues with FormFile ID
                form_field_value.value = str(form_file.id)
                form_field_value.save()

        messages.success(request, "Form data updated successfully!")

    except Exception as e:
        traceback.print_exc()
        messages.error(request, "Oops...! Something went wrong!")

    finally:
        return redirect("/masters?entity=form_master&type=i")