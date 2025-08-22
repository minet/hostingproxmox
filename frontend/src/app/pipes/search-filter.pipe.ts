import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'filter',
  standalone: false
})
export class SearchFilterPipe implements PipeTransform {

  transform(items: any[], searchText: any): any[] {
    if (!items) return [];
    if (!searchText) return items;

    const searchStr = searchText.toString().toLowerCase();
    
    return items.filter(item => {
      // If it's a string, search directly
      if (typeof item === 'string') {
        return item.toLowerCase().includes(searchStr);
      }
      
      // If it's an object, search through all properties
      if (typeof item === 'object' && item !== null) {
        return this.searchInObject(item, searchStr);
      }
      
      // For other types, convert to string and search
      return item.toString().toLowerCase().includes(searchStr);
    });
  }

  private searchInObject(obj: any, searchStr: string): boolean {
    for (const key in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        const value = obj[key];
        
        if (value === null || value === undefined) {
          continue;
        }
        
        // Search in nested objects
        if (typeof value === 'object' && !Array.isArray(value)) {
          if (this.searchInObject(value, searchStr)) {
            return true;
          }
        } else if (Array.isArray(value)) {
          // Search in array elements
          if (value.some(item => this.searchInObject({ temp: item }, searchStr))) {
            return true;
          }
        } else {
          // Search in primitive values
          if (value.toString().toLowerCase().includes(searchStr)) {
            return true;
          }
        }
      }
    }
    return false;
  }
}
