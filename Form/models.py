from django.db import models

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
    form = models.ForeignKey('Form.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='fields')
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
    field = models.ForeignKey('Form.FormField',null=True, blank=True, on_delete=models.CASCADE, related_name='validations')
    form = models.ForeignKey('Form.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='form_validations')
    sub_master =  models.ForeignKey('Form.ValidationMaster',null=True, blank=True, on_delete=models.CASCADE, related_name='field_validations')
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

class FormFieldValues(models.Model):
    form = models.ForeignKey('Form.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='form_data')
    form_data = models.ForeignKey('Form.FormData',null=True, blank=True, on_delete=models.CASCADE, related_name='form_value_id')
    field = models.ForeignKey('Form.FormField',null=True, blank=True, on_delete=models.CASCADE, related_name='field_value_id')
    value = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form_field_values'

class FormFile(models.Model):
    file_name = models.TextField(null=True, blank=True)
    uploaded_name = models.TextField(null=True, blank=True)
    file_path = models.TextField(null=True, blank=True)
    file = models.ForeignKey('Form.FormFieldValues',null=True, blank=True, on_delete=models.CASCADE, related_name='file_id')
    form = models.ForeignKey('Form.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='form_filr_id')
    field = models.ForeignKey('Form.FormField',null=True, blank=True, on_delete=models.CASCADE, related_name='field_file_id')
    form_data = models.ForeignKey('Form.FormData',null=True, blank=True, on_delete=models.CASCADE, related_name='form_data_id')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form_file'

class FormData(models.Model):
    form = models.ForeignKey('Form.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='form_data_id')
    req_no = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form_data'



