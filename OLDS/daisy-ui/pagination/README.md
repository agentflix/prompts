
# Pagination Component

This component provides a group of buttons that allow the user to navigate between a set of related content. It leverages the `daisy-join` component for styling.

## Usage

```html
<daisy-pagination
  [currentPage]="currentPage"
  [totalPages]="totalPages"
  (pageChange)="onPageChange($event)"
></daisy-pagination>
```

## Inputs

- `currentPage`: `number` - The currently active page number. Defaults to `1`.
- `totalPages`: `number` - The total number of pages available. Defaults to `1`.
- `range`: `number` - The number of page buttons to show around the current page. Defaults to `2`.
- `size`: `PaginationSize | null` - The size of the pagination buttons. Can be `xs`, `sm`, `md`, `lg`, or `xl`.
- `customClass`: `string` - Custom classes to add to the pagination container.

## Outputs

- `pageChange`: `EventEmitter<number>` - Emits the new page number when a page button is clicked.

## Example

```typescript
import { Component } from '@angular/core';
import { PaginationComponent } from './daisy-ui/pagination/pagination.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [PaginationComponent],
  template: `
    <div class="flex flex-col gap-4 items-center">
      <daisy-pagination
        [currentPage]="currentPage"
        [totalPages]="10"
        [range]="1"
        [size]="'lg'"
        (pageChange)="onPageChange($event)"
      ></daisy-pagination>
      <p>Current Page: {{ currentPage }}</p>
    </div>
  `,
})
export class AppComponent {
  currentPage = 3;

  onPageChange(newPage: number): void {
    this.currentPage = newPage;
    console.log('Navigated to page:', newPage);
  }
}
```
