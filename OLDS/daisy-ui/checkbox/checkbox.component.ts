
import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  Input,
  Output,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

export type CheckboxColor =
  | 'primary'
  | 'secondary'
  | 'accent'
  | 'neutral'
  | 'info'
  | 'success'
  | 'warning'
  | 'error';
export type CheckboxSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'daisy-checkbox',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <input
      type="checkbox"
      [class]="classes"
      [checked]="checked"
      [disabled]="disabled"
      [indeterminate]="indeterminate"
      (change)="onCheckedChange($event)"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CheckboxComponent {
  @Input() checked = false;
  @Input() disabled = false;
  @Input() indeterminate = false;
  @Input() color: CheckboxColor | null = null;
  @Input() size: CheckboxSize | null = null;
  @Input() customClass = '';

  @Output() checkedChange = new EventEmitter<boolean>();

  get classes(): string {
    const baseClasses = 'checkbox';
    const colorClass = this.color ? `checkbox-${this.color}` : '';
    const sizeClass = this.size ? `checkbox-${this.size}` : '';

    return [baseClasses, colorClass, sizeClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }

  onCheckedChange(event: Event): void {
    const isChecked = (event.target as HTMLInputElement).checked;
    this.checkedChange.emit(isChecked);
  }
}
