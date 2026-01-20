
import { ChangeDetectionStrategy, Component, Input, Output, EventEmitter, forwardRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, NG_VALUE_ACCESSOR, ControlValueAccessor } from '@angular/forms';

export type SelectColor =
  | 'neutral'
  | 'primary'
  | 'secondary'
  | 'accent'
  | 'info'
  | 'success'
  | 'warning'
  | 'error';
export type SelectSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface SelectOption {
  value: any;
  label: string;
  disabled?: boolean;
}

@Component({
  selector: 'daisy-select',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <select
      [class]="classes"
      [disabled]="disabled"
      [(ngModel)]="selectedValue"
      (change)="onSelectChange($event)"
      (blur)="onTouched()"
    >
      @if (placeholder) {
        <option [value]="null" disabled selected>{{ placeholder }}</option>
      }
      @for (option of options; track option.value) {
        <option [value]="option.value" [disabled]="option.disabled">{{ option.label }}</option>
      }
    </select>
  `,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => SelectComponent),
      multi: true,
    },
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SelectComponent implements ControlValueAccessor {
  @Input() options: SelectOption[] = [];
  @Input() placeholder: string | null = null;
  @Input() color: SelectColor | null = null;
  @Input() size: SelectSize | null = null;
  @Input() ghost = false;
  @Input() disabled = false;
  @Input() customClass = '';

  selectedValue: any = null;
  onChange: any = () => {};
  onTouched: any = () => {};

  get classes(): string {
    const baseClasses = 'select';
    const colorClass = this.color ? `select-${this.color}` : '';
    const sizeClass = this.size ? `select-${this.size}` : '';
    const ghostClass = this.ghost ? 'select-ghost' : '';

    return [
      baseClasses,
      colorClass,
      sizeClass,
      ghostClass,
      this.customClass,
    ]
      .filter(Boolean)
      .join(' ');
  }

  writeValue(obj: any): void {
    this.selectedValue = obj;
  }

  registerOnChange(fn: any): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: any): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }

  onSelectChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    this.selectedValue = target.value;
    this.onChange(this.selectedValue);
  }
}
