# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Advanced Odoo Chatter',
    'version': '17.0.1.0.0',
    'live_test_url': 'https://youtu.be/4-QMvoQjwTg',
    'sequence': 1,
    'summary': """Advanced Chatter, All in one chatter, Chatter FormView, Chatter Form View, Chatter in Form, FormView Chatter, Form View Chatter, 
                Chatter History Visibility, Chatter Log Visibility, Chatter Logs Visibility, Chatter Note Visibility, Chatter Notes Visibility, 
                Chatter Message Visibility, Chatter Messages Visibility, Chatter Activities Visibility, Chatter Activity Visibility, Chatter Toolbar,
                Web Backend Chatter, Web Responsive Chatter, Mail Message in Chatter, Mail Messages in Chatter, Chatter Panel, ChatterPanel,
                Edit/Delete Messages, Edit/Delete Notes, Edit/Delete Activities, Edit Messages, Edit Notes, Edit Activities, Chat Panel, SidePanel Chatter,
                Show/Hide Messages, Show/Hide Notes, Show/Hide Activities, Delete Messages, Delete Notes, Delete Activities, ChatPanel, Side Panel, 
                Live Chat, Live Chatter Preview, Accidental Live Chat, Accidental Chatter Preview, Preview Message History, Chatter Timeline, Side Chatter,
                Schedule Activities, Activity Planning, Log note, Log a note, Send message, Editable message, Chatter position right, Email Message,
                EMail Management, Mail message management, note management, activity management, Chatter position right, Chatter sided, Sidebar Chatter,
                Chatter right, Chatter sticky position right, Chatter fixed position right, Chatter freeze position right, Chatter frozen position right,
                Show/Hide Chatter, Show Chatter, Hide Chatter, Toggle Chatter, Toggle Message, Toggle Note, Toggle Activity, Toggle Activities,SideChatter,
                Show/Hide Notification, Show/Hide Notifications, Show Notification, Show Note, Show Message, Show Activity, Mail Attachment Preview,
                Chatter Notification Visibility, Edit/Delete Notification, Edit Notification, Delete Notification, Preview Notification History,
                Chatter Notifications Visibility, Edit/Delete Notifications, Edit Notifications, Delete Notifications, Preview Notifications History,
                Preview Note History, Preview Activity History, Preview Messages History, Preview Notes History, Preview Activities History""",
    'description': "It's time to bid goodbye to the boring, monotonous chatter of Odoo which you have been using for a while and say hello to an advanced chatter, which breathes life into your Odoo backend.",
    'author': 'Innoway',
    'maintainer': 'Innoway',
    'price': '60.0',
    'currency': 'EUR',
    'website': 'https://innoway-solutions.com',
    'license': 'OPL-1',
    'images': [
        'static/description/wallpaper.png'
    ],
    'depends': [
        'mail'
    ],
    'data': [
        
    ],
    'assets': {
        'web.assets_backend': [
            'odoo_chatter/static/src/xml/toolbar.xml',
            'odoo_chatter/static/src/scss/toolbar.scss',
            'odoo_chatter/static/src/js/toolbar.js',
        ],
    },
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
