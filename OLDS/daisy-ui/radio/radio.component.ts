
import { ChangeDetectionStrategy, Component, Input, Output, EventEmitter, forwardRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, NG_VALUE_ACCESSOR, ControlValueAccessor } from '@angular/forms';

export type RadioColor =
  | 'neutral'
  | 'primary'
  | 'secondary'
  | 'accent'
  | 'success'
  | 'warning'
  | 'info'
  | 'error';
export type RadioSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'daisy-radio',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <input
      type="radio"
      [name]="name"
      [value]="value"
      [checked]="checked"
      [disabled]="disabled"
      [class]="classes"
      (change)="onRadioChange($event)"
      (blur)="onTouched()"
    />
  `,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => RadioComponent),
      multi: true,
    },
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RadioComponent implements ControlValueAccessor {
  @Input() name!: string;
  @Input() value: any;
  @Input() checked = false;
  @Input() disabled = false;
  @Input() color: RadioColor | null = null;
  @Input() size: RadioSize | null = null;
  @Input() customClass = '';

  onChange: any = () => {};
  onTouched: any = () => {};

  get classes(): string {
    const baseClasses = 'radio';
    const colorClass = this.color ? `radio-${this.color}` : '';
    const sizeClass = this.size ? `radio-${this.size}` : '';

    return [baseClasses, colorClass, sizeClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }

  writeValue(obj: any): void {
    this.checked = (obj === this.value);
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

  onRadioChange(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (target.checked) {
      this.onChange(this.value);
    }
  }
}
