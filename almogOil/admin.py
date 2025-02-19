from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password
from almogOil import models

# Custom form to handle password hashing
class UserPasswordForm(forms.ModelForm):
    class Meta:
        fields = '__all__'

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            return password  # Keeping it as plain text; will be hashed before saving
        return None

# Generic admin class for handling password hashing
class UserPasswordAdmin(admin.ModelAdmin):
    form = UserPasswordForm
    list_display = ('username', 'password')

    def save_model(self, request, obj, form, change):
        """Override the save_model method to hash the password before saving."""
        if obj.password:
            obj.set_password(obj.password)  # Hash the password
        super().save_model(request, obj, form, change)

# Apply password hashing to EmployeesTable
class EmployeesTableAdmin(UserPasswordAdmin):
    list_display = ('employee_id', 'name', 'salary', 'start_date', 'end_date', 'active', 'category', 'username', 'password')

# Apply password hashing to AllClientsTable
class AllClientsTableAdmin(UserPasswordAdmin):
    list_display = ('clientid', 'username', 'password')

# Apply password hashing to AllSourcesTable
class AllSourcesTableAdmin(UserPasswordAdmin):
    list_display = ('clientid', 'username', 'password')

# Registering models
admin.site.register(models.MeasurementsTable)
admin.site.register(models.Mainitem)
admin.site.register(models.EmployeesTable, EmployeesTableAdmin)
admin.site.register(models.AllClientsTable, AllClientsTableAdmin)
admin.site.register(models.AllSourcesTable, AllSourcesTableAdmin)

from django.contrib import admin
from django.apps import apps
from django.contrib.auth.models import AbstractBaseUser

# Get all models from your app
app_models = apps.get_app_config('almogOil').get_models()

# List of models to exclude (Django built-in auth models)
excluded_models = {
    'AuthGroup', 'AuthGroupPermissions', 'AuthPermission', 'AuthUser',
    'AuthUserGroups', 'AuthUserUserPermissions', 'DjangoAdminLog',
    'DjangoContentType', 'DjangoMigrations', 'DjangoSession'
}

# Register each model dynamically, except Django's built-in ones
for model in app_models:
    if not issubclass(model, AbstractBaseUser) and model.__name__ not in excluded_models:
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass  # Skip already registered models
