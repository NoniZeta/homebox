import * as _ from "lodash";
import {Pipe, PipeTransform} from "@angular/core";

@Pipe({
    name: "numericFilter"
})
export class NumericFilterPipe implements PipeTransform {

    transform(array: any[], query: string): any {
        if (query) {
            return _.filter(array, row=>row.key_ordre.indexOf(query) > -1);
        }
        return array;
    }
}