import * as _ from "lodash";
import {Pipe, PipeTransform} from "@angular/core";
import { Word } from './Word';

@Pipe({
    name: "noMappingFilter"
})
export class NoMappingFilterPipe implements PipeTransform {

    transform(array: any[], query: boolean): any {
        if (query) {
            return _.filter(array, (row:Word)=>{
                    let result = true;
                    if(query){
                        result =  row.vocal.length == 0 || row.isModified ;
                    } 
                    return result;
                });
        }
        return array;
    }
}