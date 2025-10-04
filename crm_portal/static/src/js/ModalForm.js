/** @odoo-module **/

import {Component, useState} from '@odoo/owl';
import { useService } from "@web/core/utils/hooks";

export class ModalForm extends Component {
    static template = 'crm_portal.ModalFormTemplate';

     setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        this.state = useState({
            isVisible: false,
        });
    }


    openCRM() {
        console.log('Open clicked...');
        this.state.isVisible = true;
    }

    closeModal() {
        console.log('Close clicked...');
        this.state.isVisible = false;
    }

    onOutsideClick(event) {
        const modal = this.el.querySelector('.form-popup-bg');
        if (event.target === modal) {
            this.closeModal();
        }
    }
}
