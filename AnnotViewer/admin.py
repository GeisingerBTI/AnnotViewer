#!/usr/bin/env python

__author__ = "Brandon Geise"
__copyright__ = "Copyright 2016, Geisinger Health System"
__license__ = "Apache 2.0"

from flask import Flask, url_for, redirect, request, current_app
from flask_admin import Admin, AdminIndexView, menu, BaseView
from flask_admin.contrib.sqla import ModelView
from AnnotViewer import app, models, db, views
from flask.ext.login import current_user


class MyBaseView(AdminIndexView):
    def is_accessible(self):
        if not current_user.is_authenticated or not current_user.is_active:
            return False

        if current_user.is_admin().upper() == 'ADMIN':
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                return("<p>You don't have permissions to view this area</p>")
            else:
                # login
                return redirect(url_for('login', next=request.url))


class UserAdmin(ModelView):
    column_exclude_list = ['tables']
    form_excluded_columns = ['tables']
    column_labels = dict(username='User Name',activeYN='Active', user_role='User Role')
    form_choices = { 'user_role' : [('admin','admin'),('user','user')]}

class TableAdmin(ModelView):
    column_labels = dict(databaseName='Database Name',tableName='Table Name', userID='User Name')
    column_sortable_list = ('databaseName','tableName',('userID', models.User.username))

try:
    script_root = "/" + app.config["ROOT"] + "/"
except:
    script_root = "/"


admin = Admin(app,name="Admin Area", base_template='layout.html',template_mode="bootstrap3", index_view=MyBaseView(name='Home', template='admin/index.html'))
admin.add_view(UserAdmin(models.User, db.session))
admin.add_view(TableAdmin(models.Tables, db.session))
admin.add_link(menu.MenuLink(name='Back Home', url=script_root))
admin.add_link(menu.MenuLink(name='Logout', url=script_root + "logout"))
