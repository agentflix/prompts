
import { ChangeDetectionStrategy, Component, Input, Output, EventEmitter, forwardRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, NG_VALUE_ACCESSOR, ControlValueAccessor } from '@angular/forms';

export type RatingSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'daisy-rating',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="rating" [class]="classes">
      @if (hidden) {
        <input
          type="radio"
          [name]="name"
          class="rating-hidden"
          [attr.aria-label]="'clear'"
          [checked]="!value"
          (change)="onRatingChange(0)"
        />
      }
      @for (star of stars; track star) {
        <input
          type="radio"
          [name]="name"
          [class]="getStarClasses(star)"
          [attr.aria-label]="getAriaLabel(star)"
          [checked]="value === star"
          (change)="onRatingChange(star)"
        />
      }
    </div>
  `,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => RatingComponent),
      multi: true,
    },
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RatingComponent implements ControlValueAccessor {
  @Input() name!: string;
  @Input() value: number = 0;
  @Input() max = 5;
  @Input() half = false;
  @Input() hidden = false;
  @Input() size: RatingSize | null = null;
  @Input() colorClass: string | null = null; // e.g., 'bg-orange-400'
  @Input() customClass = '';

  onChange: any = () => {};
  onTouched: any = () => {};

  get stars(): number[] {
    if (this.half) {
      const halfStars = [];
      for (let i = 1; i <= this.max * 2; i++) {
        halfStars.push(i * 0.5);
      }
      return halfStars;
    }
    return Array.from({ length: this.max }, (_, i) => i + 1);
  }

  get classes(): string {
    const sizeClass = this.size ? `rating-${this.size}` : '';
    const halfClass = this.half ? 'rating-half' : '';
    return [sizeClass, halfClass, this.customClass].filter(Boolean).join(' ');
  }

  getStarClasses(starValue: number): string {
    const baseClasses = 'mask mask-star-2';
    const halfClass = this.half ? (starValue % 1 === 0 ? 'mask-half-2' : 'mask-half-1') : '';
    return [baseClasses, halfClass, this.colorClass].filter(Boolean).join(' ');
  }

  getAriaLabel(starValue: number): string {
    return `${starValue} star`;
  }

  writeValue(obj: any): void {
    this.value = obj;
  }

  registerOnChange(fn: any): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: any): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    // Not directly supported by DaisyUI rating, but can be handled with custom CSS or by disabling inputs
  }

  onRatingChange(newValue: number): void {
    this.value = newValue;
    this.onChange(this.value);
  }
}
