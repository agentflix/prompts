
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { JoinComponent, JoinItemDirective } from '../join/join.component';

export type PaginationSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'daisy-pagination',
  standalone: true,
  imports: [CommonModule, JoinComponent, JoinItemDirective],
  template: `
    <daisy-join [customClass]="customClass">
      <button daisyJoinItem class="btn" [class.btn-disabled]="currentPage === 1" (click)="goToPage(currentPage - 1)">«</button>
      @for (page of pages; track page) {
        <button
          daisyJoinItem
          class="btn"
          [class.btn-active]="page === currentPage"
          (click)="goToPage(page)"
        >
          {{ page }}
        </button>
      }
      <button daisyJoinItem class="btn" [class.btn-disabled]="currentPage === totalPages" (click)="goToPage(currentPage + 1)">»</button>
    </daisy-join>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PaginationComponent {
  @Input() currentPage = 1;
  @Input() totalPages = 1;
  @Input() range = 2; // Number of pages to show around the current page
  @Input() size: PaginationSize | null = null;
  @Input() customClass = '';

  @Output() pageChange = new EventEmitter<number>();

  get pages(): number[] {
    const pages: number[] = [];
    const startPage = Math.max(1, this.currentPage - this.range);
    const endPage = Math.min(this.totalPages, this.currentPage + this.range);

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    return pages;
  }

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
      this.pageChange.emit(page);
    }
  }
}
