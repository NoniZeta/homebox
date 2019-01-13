import * as _ from "lodash";
import {Pipe, PipeTransform} from "@angular/core";

@Pipe({
    name: "serieFilter"
})
export class SerieFilterPipe implements PipeTransform {

    transform(array: any[], query: string): any {
        if (query) {
            return _.filter(array, row=>row.key_ordre.indexOf(query) > -1);
        }
        return array;
    }
}