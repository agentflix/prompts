
import { ChangeDetectionStrategy, Component, Input, Output, EventEmitter, forwardRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, NG_VALUE_ACCESSOR, ControlValueAccessor } from '@angular/forms';

export type RangeColor =
  | 'neutral'
  | 'primary'
  | 'secondary'
  | 'accent'
  | 'success'
  | 'warning'
  | 'info'
  | 'error';
export type RangeSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'daisy-range',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <input
      type="range"
      [min]="min"
      [max]="max"
      [value]="value"
      [step]="step"
      [class]="classes"
      [disabled]="disabled"
      (input)="onRangeChange($event)"
      (blur)="onTouched()"
    />
  `,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => RangeComponent),
      multi: true,
    },
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RangeComponent implements ControlValueAccessor {
  @Input() min = 0;
  @Input() max = 100;
  @Input() value = 0;
  @Input() step: number | null = null;
  @Input() color: RangeColor | null = null;
  @Input() size: RangeSize | null = null;
  @Input() disabled = false;
  @Input() customClass = '';

  onChange: any = () => {};
  onTouched: any = () => {};

  get classes(): string {
    const baseClasses = 'range';
    const colorClass = this.color ? `range-${this.color}` : '';
    const sizeClass = this.size ? `range-${this.size}` : '';

    return [baseClasses, colorClass, sizeClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }

  writeValue(value: any): void {
    this.value = value;
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

  onRangeChange(event: Event): void {
    this.value = +(event.target as HTMLInputElement).value;
    this.onChange(this.value);
  }
}
