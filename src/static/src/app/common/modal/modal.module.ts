import { NgModule } from '@angular/core';

import { Modal } from './modal.component';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@NgModule({
    imports: [CommonModule,
        FormsModule,],
    exports: [Modal],
    declarations: [Modal],
    providers: [],
})
export class ModalModule { }
