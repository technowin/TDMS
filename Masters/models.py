from django.db import models
from django.db import models
from Account.models import *

class application_search(models.Model):
    id = models.AutoField(primary_key=True)
    name =models.TextField(null=True,blank=True)
    description =models.TextField(null=True,blank=True)
    href =models.TextField(null=True,blank=True)
    menu_id =models.TextField(null=True,blank=True)
    is_active =models.BooleanField(null=True,blank=True,default=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='app_search_created',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='app_search_updated',blank=True, null=True,db_column='updated_by')
    
    class Meta:
        db_table = 'application_search'
    def __str__(self):
        return self.name
         
class parameter_master(models.Model):
    parameter_id = models.AutoField(primary_key=True)
    parameter_name =models.TextField(null=True,blank=True)
    parameter_value =models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='parameter_created_by',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='parameter_updated_by',blank=True, null=True,db_column='updated_by')
    
    class Meta:
        db_table = 'parameter_master'
    def __str__(self):
        return self.parameter_name


class status_master(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.TextField(null=True, blank=True)
    status_type = models.TextField(null=True, blank=True)
    status_color = models.TextField(null=True, blank=True)
    is_active = models.IntegerField(default=1)  
    level = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'status_master'

class status_color(models.Model):
    id = models.AutoField(primary_key=True)
    color = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'status_color'

class document_master(models.Model):
    doc_id = models.AutoField(primary_key=True)
    doc_name = models.TextField(null=True, blank=True)
    doc_subpath =models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.TextField(null=True, blank=True)
    is_active = models.IntegerField(default=1)
    mandatory = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'document_master'


class department_master(models.Model):
    id = models.AutoField(primary_key=True)
    name =  models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'department_master'

class branch_master(models.Model):
    id = models.AutoField(primary_key=True)
    name =  models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'branch_master'

class stakeholders(models.Model):
    id = models.AutoField(primary_key=True)
    name =  models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'stakeholders'

class send_user(models.Model):
    id = models.AutoField(primary_key=True)
    name =  models.TextField(null=True, blank=True)
    email =  models.TextField(null=True, blank=True)
    mobile =  models.TextField(null=True, blank=True)
    department =  models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'send_user'       

class Log(models.Model):
    log_text = models.TextField(null=True,blank=True)
    
    class Meta:
        db_table = 'logs'

class ControlParameterMaster(models.Model):
    id = models.AutoField(primary_key=True)
    control_name = models.TextField(null=True, blank=True)
    control_value = models.TextField(null=True, blank=True)
    is_action = models.BooleanField(null=True,blank=True,default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)


    class Meta:
        db_table = 'control_parameter_master'

class ControlMaster(models.Model):
    control_id = models.AutoField(primary_key=True)
    control_type_id = models.IntegerField(null=True, blank=True)
    control_type = models.TextField(null=True, blank=True)
    control_value = models.TextField(null=True, blank=True)
    data_type = models.TextField(null=True, blank=True)
    sub_master1 = models.IntegerField(null=True, blank=True)
    sub_master2 = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'control_master'

class FormMaster(models.Model):
    form_id = models.AutoField(primary_key=True)
    form_name = models.TextField(null=True, blank=True)
    form_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form_master'


class FormFieldMaster(models.Model):
    id =  models.AutoField(primary_key=True)
    form_id =  models.IntegerField(null=True, blank=True)
    parameter_name = models.TextField(null=True, blank=True)
    label_name = models.TextField(null=True, blank=True)
    control_id = models.IntegerField(null=True, blank=True)
    order_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form_field_master'

class FieldMaster(models.Model):
    field_id = models.AutoField(primary_key=True)
    form_field_id  = models.IntegerField(null=True, blank=True)
    control_id = models.IntegerField(null=True, blank=True)
    form_id =  models.IntegerField(null=True, blank=True)
    control_master_id = models.IntegerField(null=True, blank=True)
    sub_control_id = models.IntegerField(null=True, blank=True)
    sub_value = models.TextField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'field_master'


class ControlSubMaster1(models.Model):
    id = models.AutoField(primary_key=True)
    control_id = models.IntegerField(null=True, blank=True)
    control_type_id = models.IntegerField(null=True, blank=True)
    sub_control_type = models.TextField(null=True, blank=True)
    datatype = models.TextField(null=True,blank=True)
    sub_control_value = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'control_sub_master1'


    
class Form(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form'

class FormField(models.Model):
    form = models.ForeignKey('Masters.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(max_length=255)
    field_type =  models.CharField(max_length=255,null=True, blank=True)
    values = models.TextField(null=True,blank=True)
    attributes = models.TextField(null=True,blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)  
    class Meta:
        db_table = 'form_field'

class FieldValidation(models.Model):
    field = models.ForeignKey('Masters.FormField',null=True, blank=True, on_delete=models.CASCADE, related_name='validations')
    form = models.ForeignKey('Masters.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='form_validations')
    sub_master =  models.ForeignKey('Masters.ValidationMaster',null=True, blank=True, on_delete=models.CASCADE, related_name='field_validations')
    datatype = models.TextField(null=True, blank=True)
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'field_validation'

class FieldDependency(models.Model):
    field = models.ForeignKey(FormField,null=True, blank=True, on_delete=models.CASCADE, related_name='dependencies')
    dependent_on = models.ForeignKey(FormField,null=True, blank=True, on_delete=models.CASCADE, related_name='dependent_fields')
    condition = models.CharField(max_length=255)  
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'field_dependency'

class CommonMaster(models.Model):
    id = models.AutoField(primary_key=True)
    control_value = models.TextField(null=True, blank=True)
    type = models.TextField(null=True, blank=True)
    sub_master1 = models.IntegerField(null=True, blank=True)
    sub_master2 = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'common_master'


class ValidationMaster(models.Model):
    field_type = models.TextField(null=True, blank=True)
    control_name = models.TextField(null=True, blank=True)
    datatype = models.TextField(null=True, blank=True)
    control_value = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'validation_master'

class RegexPattern(models.Model):
    input_type = models.CharField(max_length=50)
    regex_pattern = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'regex_pattern'

class FormAction(models.Model):
    name = models.TextField(null=True, blank=True)
    is_master =models.BooleanField(null=True,blank=True,default=True)
    is_active =models.BooleanField(null=True,blank=True,default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'form_action'

class FormActionField(models.Model):
    type = models.TextField(null=True, blank=True)
    label_name = models.TextField(null=True, blank=True)
    button_name = models.TextField(null=True, blank=True)
    type = models.TextField(null=True, blank=True)
    bg_color = models.TextField(null=True, blank=True)
    text_color = models.TextField(null=True, blank=True)
    button_type = models.TextField(null=True, blank=True)
    dropdown_values = models.TextField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    action = models.ForeignKey(FormAction,null=True, blank=True, on_delete=models.CASCADE, related_name='form_action')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form_action_field'

