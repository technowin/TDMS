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


def form(request):
    user = request.session.get('user_id', '')
    try:
        if request.method == "POST":
            try:
                form_name = request.POST.get("form_name", "").strip()
                parameter_name = request.POST.get("parameter_name", "").strip()
                control_id = request.POST.get("dropdown_option", "")
                
                # Standardize the parameter_name format
                label_name = re.sub(r'\s+', ' ', parameter_name).title()
                
                # Check if form_name already exists in FormMaster
                form = FormMaster.objects.filter(form_name=form_name).first()
                if not form:
                    form = FormMaster.objects.create(form_name=form_name)
                
                # Use the form_id from FormMaster
                form_id = form.form_id
                
                # Create a new record in FormFieldMaster with the same form_id
                new_form_entry = FormFieldMaster.objects.create(
                    form_id=form_id,  # Reference the existing form_id
                    parameter_name=parameter_name,
                    label_name=label_name,
                    control_id=control_id,
                    created_by=user,
                    updated_by=user
                ) 
                field_entries = []
                form_field_master_id = new_form_entry.id


                # Loop through POST data to capture all inputs dynamically
                for key, value in request.POST.items():
                    if key.startswith("dropdown_") and value:  # Handle Dropdowns
                        index = key.split("_")[1]  # Extract the unique index
                        subvalues = request.POST.getlist(f"subvalue_{index}[]")  # Get subvalues as a list
                        subvalue_str = ",".join(filter(None, subvalues))  # Convert to comma-separated string

                        control_master_id = request.POST.get(f"control_master_id_{index}") 
                        control_sub_id  = request.POST.get(f"control_sub_id_{index}") 
                        if value == "Simple":
                            result = "text"
                        elif value == "Numeric":
                            result = "number"
                        else:
                            result = value

                        print(result)  # This will output the final result


                        # Save everything in a single row
                        field_entries.append(FieldMaster(
                            control_master_id=control_master_id, 
                            form_id=form_id,
                            value=value, 
                            sub_control_id = control_sub_id,
                            sub_value=subvalue_str,
                            form_field_id = form_field_master_id,
                            control_id = control_id,
                            created_by=user,
                            updated_by=user
                        ))

                # for key, value in request.POST.items():
                #     if key.startswith("dropdown_") and value:  # Handle Dropdowns
                #         index = key.split("_")[1]  # Extract the unique index
                #         subvalues = request.POST.getlist(f"subvalue_{index}[]")  # Get subvalues as a list
                        
                #         # Format each subvalue individually and join them with a comma
                #         formatted_subvalues = ", ".join([f"Only {sub} characters are allowed" for sub in subvalues if sub])

                #         control_master_id = request.POST.get(f"control_master_id_{index}") 
                #         control_sub_id = request.POST.get(f"control_sub_id_{index}") 

                #         # Save everything in a single row
                #         field_entries.append(FieldMaster(
                #             control_master_id=control_master_id, 
                #             form_id=form_id,
                #             value=value, 
                #             sub_control_id=control_sub_id,
                #             sub_value=formatted_subvalues,  # Store formatted values
                #             form_field_id=form_field_master_id,
                #             control_id=control_id,
                #             created_by=user,
                #             updated_by=user
                #         ))

                    

                    elif key.startswith("value_"):  
                        values_list = request.POST.getlist(key) 
                        combined_values = ",".join(filter(None, values_list)) 

                        index = key.split("_")[1].replace("[]", "")  # Clean index (remove brackets if present)
                        control_master_id = request.POST.get(f"control_master_id_{index}")  

                        print(f"Processing: key={key}, control_master_id={control_master_id}, values={values_list}")  # Debugging

                        if combined_values:
                            field_entries.append(FieldMaster(
                                control_master_id=control_master_id,  # Store correct control_master_id
                                form_id=form_id,
                                form_field_id = form_field_master_id,
                                control_id = control_id,
                                value=combined_values,  # Save as comma-separated string
                                created_by=user,
                                updated_by=user,
                            ))




                    elif key.startswith("checkbox_") and value == "on":  # Handle Checkbox
                        control_master_id = request.POST.get(f"control_master_id_{key.split('_')[1]}")
                        field_entries.append(FieldMaster(
                            control_master_id=control_master_id,  # Store correct control_master_id
                            form_id=form_id,
                            form_field_id = form_field_master_id,
                            control_id = control_id,
                            value="Checked",  
                            created_by=user,
                            updated_by=user
                        ))


                    elif key.startswith("textbox_") and value:  # Handle Textbox
                        control_master_id = request.POST.get(f"control_master_id_{key.split('_')[1]}")
                        field_entries.append(FieldMaster(
                            control_master_id=control_master_id, 
                            form_id=form_id,
                            value=value,
                            form_field_id = form_field_master_id,
                            control_id = control_id,
                            created_by=user,
                            updated_by=user
                        ))


                # Bulk insert all field entries
                if field_entries:
                    FieldMaster.objects.bulk_create(field_entries)

                messages.success(request, "Form and fields saved successfully!!")

                enc_form_id = enc(str(form_id))  # Encrypt the form_id before passing
                return redirect(f'/form?form_id={enc_form_id}')

            except Exception as e:
                tb = traceback.extract_tb(e.__traceback__)
                fun = tb[0].name
                callproc("stp_error_log", [fun, str(e), user])
                messages.error(request, 'Oops...! Something went wrong!')
                return JsonResponse({"error": "Something went wrong!"}, status=500)

        else:
            id  = request.GET.get('form_id', '')
            if id:
                form_id = request.GET.get("form_id")  # Get form_id from request
                form_id = dec(form_id)# Fetch dropdown options
                

                dropdown_options = ControlParameterMaster.objects.all()
                form = FormMaster.objects.get(form_id=form_id)
                control_master = ControlMaster.objects.all()
                form_entries = FormFieldMaster.objects.filter(form_id=form_id)
                field_entries = FieldMaster.objects.filter(form_id=form_id) 

                for field in field_entries:
                    field.options_list = [option.strip() for option in field.value.split(",")] if field.value else []
                    print(field.options_list)


                return render(request, "Master/form.html", {
                    "form":form,
                    "control_master":control_master,
                    "dropdown_options": dropdown_options,
                    "form_entries": form_entries,
                    "field_entries": field_entries,
                })

            else:
                dropdown_options = ControlParameterMaster.objects.all()  
                return render(request, "Master/form.html", {"dropdown_options": dropdown_options})
    except Exception as e:
                tb = traceback.extract_tb(e.__traceback__)
                fun = tb[0].name
                callproc("stp_error_log", [fun, str(e), user])
                messages.error(request, 'Oops...! Something went wrong!')
                return JsonResponse({"error": "Something went wrong!"}, status=500)
    finally:
        Db.closeConnection()
        



def get_control_values(request):
    if request.method == "POST":
        try:
            control_value_id = request.POST.get("control_value_id")

            if control_value_id:
                print(f"Fetching control values for control_id: {control_value_id}")  # Debug

                # Fetch rows from ControlMaster
                control_values = list(ControlMaster.objects.filter(control_type_id=control_value_id)
                                      .values("control_id", "control_type_id", 
                                              "control_value", "data_type", "sub_master1"))

                response_data = []

                for control in control_values:
                    control_id = control["control_id"]
                    sub_master1 = control.get("sub_master1", 0)

                    print(f"Processing control_id: {control_id}, sub_master1: {sub_master1}")  # Debug

                    control_entry = {
                        "control_master_id": control_id,
                        "control_type_id": control["control_type_id"],
                        "control_value": control["control_value"],
                        "data_type": control["data_type"],
                        "sub_master1": sub_master1,
                        "sub_controls": []
                    }

                    # Fetch sub-controls if sub_master1 is '1'
                    if sub_master1 == 1:
                        sub_controls = list(ControlSubMaster1.objects.filter(control_id=control_id)
                                        .values("id","control_type_id", "sub_control_type", 
                                                "sub_control_value", "datatype"))

                        for sub_control in sub_controls:
                            sub_control_values = sub_control["sub_control_type"].split(",")  # Split values

                            control_entry["sub_controls"].append({
                                "control_sub_id":sub_control["id"],
                                "control_type_id": sub_control["control_type_id"],
                                "sub_control_type": sub_control["sub_control_type"],
                                "datatype": sub_control["datatype"],
                                "sub_control_value_list": sub_control_values  # Pass as a list
                            })

                    response_data.append(control_entry)

                # Pass the updated response_data to the template
                return render(request, "Master/_partialForm.html", {"control_values": response_data})

        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            fun = tb[0].name
            callproc("stp_error_log", [fun, str(e), request.user.id])
            print(f"Error: {e}")
            return JsonResponse({'result': 'fail', 'message': 'Something went wrong!'}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)




def get_control_values_data(request):
    if request.method == "GET":
        try:
            control_value_id = request.GET.get("control_value_id")
            parameter = request.GET.get("parameter")
            form_name = request.GET.get("form")

            form = FormMaster.objects.filter(form_name=form_name).first()
            if not form:
                return JsonResponse({"error": "Form not found"}, status=404)

            form_id = form.form_id

            # Get field_id from FormFieldMaster
            form_field = FormFieldMaster.objects.filter(label_name=parameter, form_id=form_id).first()
            if not form_field:
                return JsonResponse({"error": "Form field not found"}, status=404)

            field_id = form_field.id

            # Get all fields for the form
            form_fields = FormFieldMaster.objects.filter(form_id=form_id).values()

            # Fetch ControlMaster based on field_id
            control_values = []
            for field in form_fields:
                control_id = field.get("control_master_id")
                control_master = ControlMaster.objects.filter(id=control_id).first()

                if control_master:
                    sub_controls = control_master.sub_control_values.split(",") if control_master.sub_control_values else []
                    control_values.append({
                        "control_value": control_master.control_value,
                        "data_type": control_master.data_type,
                        "control_master_id": control_master.id,
                        "sub_controls": [{"sub_control_value_list": sub_controls}]
                    })

            return JsonResponse({
                "form_id": form_id,
                "control_values": control_values,
                "fields": list(form_fields)
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)





def get_sub_item(request):
    if request.method == "POST":
        try:
            sub_control_type = request.POST.get("selected_value")  # Receiving sub_control_type
            
            if sub_control_type:
                print(f"Fetching sub-control for sub_control_type: {sub_control_type}")  # Debugging

                # Fetch only one row based on sub_control_type
                sub_control = ControlSubMaster1.objects.filter(sub_control_type=sub_control_type).values(
                    "id","control_type_id", "sub_control_type", "sub_control_value", "datatype"
                ).first()  # Fetch only the first row

                if sub_control:
                    sub_control_values = sub_control["sub_control_type"].split(",")  # Split values if needed

                    response_data = {
                        "control_sub_id": sub_control["id"],
                        "control_type_id": sub_control["control_type_id"],
                        "sub_control_type": sub_control["sub_control_type"],
                        "sub_control_value": sub_control["sub_control_value"],
                        "datatype": sub_control["datatype"],
                        "sub_control_value_list": sub_control_values  # Pass as a list
                    }

                    return JsonResponse({"result": "success", "data": response_data}, status=200)
                else:
                    return JsonResponse({"result": "fail", "message": "No matching data found"}, status=404)

        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            fun = tb[0].name
            callproc("stp_error_log", [fun, str(e), request.user.id])
            print(f"Error: {e}")
            return JsonResponse({'result': 'fail', 'message': 'Something went wrong!'}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


    
def update_form(request):
    try:
        pk = request.POST.get("form_id")
        fk = request.POST.get("form_field_id")

        form = FormMaster.objects.get(form_id = pk)
        form_field_master = FormFieldMaster.objects.get(form_id=pk, id=fk)

        # Fetch the necessary fields from FieldMaster and DropdownOption
        field_master_data = FieldMaster.objects.filter(form_id=pk,form_field_id=fk)
        dropdown_options = ControlParameterMaster.objects.all()

        # Prepare the data for rendering in the template
        context = {
            'form':form,
            'form_field_master': form_field_master,
            'field_master_data': field_master_data,
            "dropdown_options": dropdown_options
        }

        return render(request, "Master/form.html", context)
        # return render(request, 'update_form_template.html', context)

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        callproc("stp_error_log", [fun, str(e), request.user.id])
        print(f"Error: {e}")
        return JsonResponse({'result': 'fail', 'message': 'Something went wrong!'}, status=500)


def delete_form(request):
    try:
        pk = request.POST.get("form_id")
        fk = request.POST.get("form_field_id")
        FormFieldMaster.objects.filter(form_id=pk,id=fk).delete()
        FieldMaster.objects.filter(form_id=pk,form_field_id=fk).delete()

        enc_form_id = enc(str(pk))  # Encrypt the form_id before passing
        return redirect(f'/form?form_id={enc_form_id}')

    except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            fun = tb[0].name
            callproc("stp_error_log", [fun, str(e), request.user.id])
            print(f"Error: {e}")
            return JsonResponse({'result': 'fail', 'message': 'Something went wrong!'}, status=500)()
    


def form_builder(request):
    form_id = request.GET.get('form_id')
    if form_id:
        form_id = dec(form_id)
        form = Form.objects.get(id = form_id)
        fields = FormField.objects.filter(form_id=form_id)
        validations = FieldValidation.objects.filter(form_id=form_id)


        # Organizing validations in a dictionary {field_id: {validation_type: value}}
        validation_dict = {}

        for validation in validations:
            field_id = validation.field.id
            sub_master_id = validation.sub_master.id
            validation_type = validation.sub_master.control_value  # Assuming 'control_value' holds validation type
            validation_value = validation.value

            # ✅ Ensure 'sub_master_id' exists in dictionary
            if sub_master_id not in validation_dict:
                validation_dict[sub_master_id] = {}

            # ✅ Ensure 'field_id' exists inside 'sub_master_id' in dictionary
            if field_id not in validation_dict[sub_master_id]:
                validation_dict[sub_master_id][field_id] = {}

            # ✅ Store validation type and its value
            validation_dict[sub_master_id][field_id][validation_type] = validation_value
  # Store type-value pair

        # Convert fields and their validation rules to JSON
        form_fields_json = json.dumps([
            {
                "id": field.id,
                "label": field.label,
                "type": field.field_type,
                "options": field.values.split(",") if field.values else [],
                "attributes":field.attributes,
                "validation": validation_dict.get(field.id, {})  # Attach validation rules
            }
            for field in fields
        ])
    common_options = list(CommonMaster.objects.filter(datatype='select').values("id","control_value"))
    sub_control = list(ValidationMaster.objects.values("id","control_name", "control_value","field_type"))
    dropdown_options = list(ControlParameterMaster.objects.values("control_name", "control_value"))
    if form_id:
        return render(request, "Master/form_builder.html", {'form': form,
            'form_fields_json': form_fields_json,
            "dropdown_options": json.dumps(dropdown_options),
            "common_options": json.dumps(common_options),
            "sub_control": json.dumps(sub_control)
        })
    else:
        return render(request, "Master/form_builder.html", {"dropdown_options": json.dumps(dropdown_options),"common_options": json.dumps(common_options),"sub_control": json.dumps(sub_control)})

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

            # Create the form
            form = Form.objects.create(name=form_name, description=form_description)

            for field in form_data:
                # Create the form field entry
                form_field = FormField.objects.create(
                    form=form,
                    label=field.get("label", ""),
                    field_type=field.get("type", ""),
                    attributes = field.get("attributes",""),
                    values=",".join(option.strip() for option in field.get("options", [])),
                )
                field_id = form_field.id

                if "subValues" in field and isinstance(field["subValues"], list):
                    for sub_value in field["subValues"]:
                        sub_master_id = sub_value.get("id")  

                        if not sub_master_id:
                            print(f"Skipping subValue without sub_master_id: {sub_value}")
                            continue

                        # 🟢 Insert FieldValidation entry
                        FieldValidation.objects.create(
                            field=get_object_or_404(FormField,id=field_id),
                            form=get_object_or_404(Form, id = form.id),  
                            sub_master_id=sub_master_id,  
                            value=sub_value.get("value", "")  # 🟢 Store the actual selected value
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
