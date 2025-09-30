/** @odoo-module **/

import {registry} from "@web/core/registry";
// Needed so that this is run after adding the menu entries
import {user_menu_items} from "@web/webclient/user_menu/user_menu_items"; // eslint-disable-line no-unused-vars
import { useDiscussSystray } from "@mail/utils/common/hooks";


registry.category("user_menuitems").remove("documentation");
registry.category("user_menuitems").remove("support");
registry.category("user_menuitems").remove("odoo_account");
registry.category("user_menuitems").remove("odoo_account");
registry.category("systray").remove("mail.activity_menu");
registry.category("systray").remove("mail.messaging_menu");


