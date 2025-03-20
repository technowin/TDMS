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


                # Loop through POST data to capture all inputs dynamically
                for key, value in request.POST.items():
                    if key.startswith("dropdown_") and value:  # Handle Dropdowns
                        index = key.split("_")[1]  # Extract the unique index
                        subvalues = request.POST.getlist(f"subvalue_{index}[]")  # Get subvalues as a list
                        subvalue_str = ",".join(filter(None, subvalues))  # Convert to comma-separated string

                        control_master_id = request.POST.get(f"control_master_id_{index}") 
                        control_sub_id  = request.POST.get(f"control_sub_id_{index}") 

                        # Save everything in a single row
                        field_entries.append(FieldMaster(
                            control_master_id=control_master_id, 
                            form_id=form_id,
                            value=value, 
                            sub_control_id = control_sub_id,
                            sub_value=subvalue_str,
                            created_by=user,
                            updated_by=user
                        ))

                    elif key.startswith("value_"):  # Handle Value Inputs
                        values_list = request.POST.getlist(key)  # Get all values as a list
                        combined_values = ",".join(filter(None, values_list))  # Join values, remove empty ones

                        if combined_values:  # Only store if there are values
                            control_master_id = request.POST.get(f"control_master_id_{key.split('_')[1]}")
                            field_entries.append(FieldMaster(
                                control_master_id=control_master_id,  # Store correct control_master_id
                                form_id=form_id,
                                value=combined_values,  # Save as comma-separated string
                                created_by=user,
                                updated_by=user
                            ))

                    elif key.startswith("checkbox_") and value == "on":  # Handle Checkbox
                        control_master_id = request.POST.get(f"control_master_id_{key.split('_')[1]}")
                        field_entries.append(FieldMaster(
                            control_master_id=control_master_id,  # Store correct control_master_id
                            form_id=form_id,
                            value="Checked",  # Save as 'Checked'
                            created_by=user,
                            updated_by=user
                        ))

                    elif key.startswith("textbox_") and value:  # Handle Textbox
                        control_master_id = request.POST.get(f"control_master_id_{key.split('_')[1]}")
                        field_entries.append(FieldMaster(
                            control_master_id=control_master_id, 
                            form_id=form_id,
                            value=value,
                            created_by=user,
                            updated_by=user
                        ))

                # Bulk insert all field entries
                if field_entries:
                    FieldMaster.objects.bulk_create(field_entries)

                messages.success(request, "Form and fields saved successfully!!")

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
                form_entries = FormFieldMaster.objects.filter(form_id=form_id)
                field_entries = FieldMaster.objects.filter(form_id=form_id) if form_id else []

                # Split field values into a list
                for field in field_entries:
                    field.options_list = field.value.split(",") if field.value else [] 


                return render(request, "Master/form.html", {
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
        if request.method=="POST":
            new_url = f'/masters?entity=form&type=i'
            return redirect(new_url) 
        



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
                    if sub_master1 == '1':
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

