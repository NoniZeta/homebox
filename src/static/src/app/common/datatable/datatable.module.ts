import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { DataTable } from './DataTable';
import { BootstrapPaginator } from './BootstrapPaginator';
import { DefaultSorter } from './DefaultSorter';
import { Paginator } from './Paginator';

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        HttpModule
    ],
    declarations: [
        DataTable,
        BootstrapPaginator,
        DefaultSorter,
        Paginator
    ],
    exports: [
        DataTable,
        BootstrapPaginator,
        DefaultSorter,
        Paginator
    ],
    providers: [
    ]
})
export class DataTableModule { }