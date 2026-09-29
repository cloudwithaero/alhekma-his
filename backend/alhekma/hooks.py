app_name = "alhekma"
app_title = "Al Hekma Hospital"
app_publisher = "Al Hekma Hospital"
app_description = "Custom ERPNext application for Al Hekma Hospital HIS"
app_email = "admin@alhekma.local"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "alhekma",
# 		"logo": "/assets/alhekma/logo.png",
# 		"title": "Al Hekma Hospital",
# 		"route": "/alhekma",
# 		"has_permission": "alhekma.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/alhekma/css/alhekma.css"
# app_include_js = "/assets/alhekma/js/alhekma.js"

# include js, css files in header of web template
# web_include_css = "/assets/alhekma/css/alhekma.css"
# web_include_js = "/assets/alhekma/js/alhekma.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "alhekma/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "alhekma/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "alhekma.utils.jinja_methods",
# 	"filters": "alhekma.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "alhekma.install.before_install"
# after_install = "alhekma.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "alhekma.uninstall.before_uninstall"
# after_uninstall = "alhekma.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "alhekma.utils.before_app_install"
# after_app_install = "alhekma.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "alhekma.utils.before_app_uninstall"
# after_app_uninstall = "alhekma.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "alhekma.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["alhekma.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes


doctype_tree_js = {
    "Healthcare Service Unit": "public/js/healthcare_service_unit_tree.js"
}
# Document Events
# ---------------
# Hook on document methods and events
# Hook on document methods and events
doc_events = {
    "Medication Request": {
        "on_update": [
            "alhekma.api.test_ward_notifications.notify_ward_nurses_on_medication_request"
        ]
    }
}
# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"alhekma.tasks.all"
# 	],
# 	"daily": [
# 		"alhekma.tasks.daily"
# 	],
# 	"hourly": [
# 		"alhekma.tasks.hourly"
# 	],
# 	"weekly": [
# 		"alhekma.tasks.weekly"
# 	],
# 	"monthly": [
# 		"alhekma.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "alhekma.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "alhekma.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "alhekma.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["alhekma.utils.before_request"]
# after_request = ["alhekma.utils.after_request"]

# Job Events
# ----------
# before_job = ["alhekma.utils.before_job"]
# after_job = ["alhekma.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"alhekma.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


override_doctype_class = {
    "Healthcare Service Unit": "alhekma.overrides.healthcare_service_unit.AlHekmaHealthcareServiceUnit"
}
