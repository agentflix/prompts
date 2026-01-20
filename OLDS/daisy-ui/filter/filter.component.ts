
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

export interface FilterOption {
  label: string;
  value: string;
}

@Component({
  selector: 'daisy-filter',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="filter">
      @if (selectedOption) {
      <button class="btn btn-square" (click)="resetFilter()">×</button>
      }
      @for (option of options; track option.value) {
      <input
        type="radio"
        [name]="name"
        [attr.aria-label]="option.label"
        class="btn"
        [value]="option.value"
        [(ngModel)]="selectedOption"
        (change)="onSelectionChange()"
      />
      }
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FilterComponent {
  @Input() options: FilterOption[] = [];
  @Input() name = 'filter-group';
  @Input() selectedOption: string | null = null;
  @Input() customClass = '';

  @Output() selectionChange = new EventEmitter<string | null>();

  onSelectionChange(): void {
    this.selectionChange.emit(this.selectedOption);
  }

  resetFilter(): void {
    this.selectedOption = null;
    this.selectionChange.emit(null);
  }
}
