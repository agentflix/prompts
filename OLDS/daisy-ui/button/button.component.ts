
import {
  ChangeDetectionStrategy,
  Component,
  HostBinding,
  Input,
} from '@angular/core';
import { CommonModule } from '@angular/common';

export type ButtonColor =
  | 'neutral'
  | 'primary'
  | 'secondary'
  | 'accent'
  | 'ghost'
  | 'link'
  | 'info'
  | 'success'
  | 'warning'
  | 'error';
export type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
export type ButtonStyle = 'outline' | 'dash' | 'soft';
export type ButtonShape = 'square' | 'circle';

@Component({
  selector: 'button[daisy-button], a[daisy-button]',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (loading) {
    <span class="loading loading-spinner"></span>
    }
    <ng-content></ng-content>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ButtonComponent {
  @Input() color: ButtonColor | null = null;
  @Input() size: ButtonSize | 'responsive' | null = 'md';
  @Input() style: ButtonStyle | null = null;
  @Input() shape: ButtonShape | null = null;
  @Input() wide = false;
  @Input() block = false;
  @Input() disabled = false;
  @Input() loading = false;
  @Input() customClass = '';

  @HostBinding('class')
  get classes(): string {
    const sizeClass =
      this.size === 'responsive'
        ? 'btn-xs sm:btn-sm md:btn-md lg:btn-lg xl:btn-xl'
        : this.size
        ? `btn-${this.size}`
        : '';

    const baseClasses = 'btn';
    const colorClass = this.color ? `btn-${this.color}` : '';
    const styleClass = this.style ? `btn-${this.style}` : '';
    const shapeClass = this.shape ? `btn-${this.shape}` : '';
    const wideClass = this.wide ? 'btn-wide' : '';
    const blockClass = this.block ? 'btn-block' : '';
    const disabledClass = this.disabled || this.loading ? 'btn-disabled' : '';

    return [
      baseClasses,
      sizeClass,
      colorClass,
      styleClass,
      shapeClass,
      wideClass,
      blockClass,
      disabledClass,
      this.customClass,
    ]
      .filter(Boolean)
      .join(' ');
  }
}
