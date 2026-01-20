
import { ChangeDetectionStrategy, Component, Input, Output, EventEmitter, forwardRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, NG_VALUE_ACCESSOR, ControlValueAccessor } from '@angular/forms';

export type InputType =
  | 'text'
  | 'password'
  | 'email'
  | 'number'
  | 'date'
  | 'datetime-local'
  | 'week'
  | 'month'
  | 'tel'
  | 'url'
  | 'search'
  | 'time';
export type InputColor =
  | 'neutral'
  | 'primary'
  | 'secondary'
  | 'accent'
  | 'info'
  | 'success'
  | 'warning'
  | 'error';
export type InputSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'daisy-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <input
      [type]="type"
      [placeholder]="placeholder"
      [value]="value"
      [class]="classes"
      [disabled]="disabled"
      (input)="onInput($event)"
      (blur)="onTouched()"
    />
  `,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => InputComponent),
      multi: true,
    },
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InputComponent implements ControlValueAccessor {
  @Input() type: InputType = 'text';
  @Input() placeholder = '';
  @Input() color: InputColor | null = null;
  @Input() size: InputSize | null = null;
  @Input() ghost = false;
  @Input() disabled = false;
  @Input() customClass = '';

  value: any = '';
  onChange: any = () => {};
  onTouched: any = () => {};

  get classes(): string {
    const baseClasses = 'input';
    const colorClass = this.color ? `input-${this.color}` : '';
    const sizeClass = this.size ? `input-${this.size}` : '';
    const ghostClass = this.ghost ? 'input-ghost' : '';

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

  onInput(event: Event): void {
    this.value = (event.target as HTMLInputElement).value;
    this.onChange(this.value);
  }
}
