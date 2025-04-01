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
from Account.db_utils import callproc
from django.views.decorators.csrf import csrf_exempt
import os
from django.urls import reverse
from TDMS.settings import *
import logging
from django.http import FileResponse, Http404
import mimetypes
logger = logging.getLogger(__name__)

@login_required
def masters(request):
    pre_url = request.META.get('HTTP_REFERER')
    header, data = [], []
    entity,type,name,id,text_name,dpl,dp,em,mb = '','','','','','','','',''
    try:
        if request.user.is_authenticated ==True:                
                global user,role_id
                user = request.user.id    
                role_id = request.user.role_id 
        if request.method=="GET":
            entity = request.GET.get('entity', '')
            type = request.GET.get('type', '')
            datalist1= callproc("stp_get_masters",[entity,type,'name',user])
            name = datalist1[0][0]
            header = callproc("stp_get_masters", [entity, type, 'header',user])
            rows = callproc("stp_get_masters",[entity,type,'data',user])
            if entity == 'su':
                dpl = callproc("stp_get_dropdown_values",['dept'])
            id = request.GET.get('id', '')
            if type=='ed' and id != '0':
                if id != '0' and id != '':
                    id = dec(id)
                rows = callproc("stp_get_masters",[entity,type,'data',id])
                text_name = rows[0][0]
                if entity == 'su':
                    em = rows[0][1]
                    mb = rows[0][2]
                    dp = rows[0][3]
                id = enc(id)
            data = []
            for row in rows:
                encrypted_id = enc(str(row[0]))
                data.append((encrypted_id,) + row[1:])

        if request.method=="POST":
            entity = request.POST.get('entity', '')
            id = request.POST.get('id', '')
            dp = request.POST.get('dp', '')
            em = request.POST.get('em', '')
            mb = request.POST.get('mb', '')
            if id != '0' and id != '':
                id = dec(id)
            name = request.POST.get('text_name', '')
            if entity == 'su':
                datalist1= callproc("stp_post_user_masters",[id,name,em,mb,dp,user])
            else: datalist1= callproc("stp_post_masters",[entity,id,name,user])

            if datalist1[0][0] == 'insert':
                messages.success(request, 'Data inserted successfully !')
            elif datalist1[0][0] == 'update':
                messages.success(request, 'Data updated successfully !')
            elif datalist1[0][0] == 'exist':
                messages.error(request, 'Data already exist !')
            
                          
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        callproc("stp_error_log",[fun,str(e),user])  
        messages.error(request, 'Oops...! Something went wrong!')
    finally:
        Db.closeConnection()
        if request.method=="GET":
            return render(request,'Master/index.html',
              {'entity':entity,'type':type,'name':name,'header':header,'data':data,
              'id':id,'text_name':text_name,'dp':dp,'em':em,'mb':mb,'dpl':dpl})
        elif request.method=="POST":  
            new_url = f'/masters?entity={entity}&type=i'
            return redirect(new_url) 
 
def sample_xlsx(request):
    pre_url = request.META.get('HTTP_REFERER')
    response =''
    global user
    user  = request.session.get('user_id', '')
    try:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = 'Sample Format'
        columns = []
        if request.method=="GET":
            entity = request.GET.get('entity', '')
            type = request.GET.get('type', '')
        if request.method=="POST":
            entity = request.POST.get('entity', '')
            type = request.POST.get('type', '')
        file_name = {'em': 'Employee Master','sm': 'Worksite Master','cm': 'Company Master','r': 'Roster'}[entity]
        columns = callproc("stp_get_masters", [entity, type, 'sample_xlsx',user])
        if columns and columns[0]:
            columns = [col[0] for col in columns[0]]

        black_border = Border(
            left=Side(border_style="thin", color="000000"),
            right=Side(border_style="thin", color="000000"),
            top=Side(border_style="thin", color="000000"),
            bottom=Side(border_style="thin", color="000000")
        )
        
        for col_num, header in enumerate(columns, 1):
            cell = sheet.cell(row=1, column=col_num)
            cell.value = header
            cell.font = Font(bold=True)
            cell.border = black_border
        
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter  
            for cell in col:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
                    
            adjusted_width = max_length + 2 
            sheet.column_dimensions[column].width = adjusted_width  
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="' + str(file_name) +" "+str(datetime.now().strftime("%d-%m-%Y")) + '.xlsx"'
        workbook.save(response)
    
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        callproc("stp_error_log",[fun,str(e),user])  
        messages.error(request, 'Oops...! Something went wrong!')
    finally:
        return response      


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
        return render(request, "Master/form_builder.html", {
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
        return render(request, "Master/form_builder.html", {
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

    return render(request, "Master/form_builder.html", {
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

                # ✅ Save `subValues` (Existing Logic)
                if "subValues" in field and isinstance(field["subValues"], list):
                    for sub_value in field["subValues"]:
                        sub_master_id = sub_value.get("id")

                        if not sub_master_id:
                            print(f"Skipping subValue without sub_master_id: {sub_value}")
                            continue

                        FieldValidation.objects.create(
                            field=get_object_or_404(FormField, id=field_id),
                            form=get_object_or_404(Form, id=form.id),
                            sub_master_id=sub_master_id,
                            value=sub_value.get("value", ""),
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
                sub_values = field.get("subValues", [])
                if not isinstance(sub_values, list):
                    continue

                for sub_value in sub_values:
                    sub_master_id = sub_value.get("id")

                    if not sub_master_id:
                        continue

                    FieldValidation.objects.create(
                        field=form_field,
                        form=form,
                        sub_master_id=sub_master_id,
                        value=sub_value.get("value", "")
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
        return render(request,  "Master/form_action_builder.html", {
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
        return render(request, "Master/form_action_builder.html", {\
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

    return render(request, "Master/form_action_builder.html", {
        "form": form,
        "master_values":master_values,
        "button_type":json.dumps(button_type),
        "form_fields_json": form_fields_json,
        "dropdown_options": json.dumps(dropdown_options),
    })



@csrf_exempt
def save_form_action(request):
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
                field_type = field.get("type", "").strip()
                
                if field_type == "button":
                    label_name = None
                    dropdown_values = None
                    bg_color = field.get("bg_color", "")
                    text_color = field.get("text_color", "")
                    status = field.get("status",None).strip()
                    button_name = field.get("value", "").strip()
                else:
                    label_name = field.get("label", "").strip()
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


