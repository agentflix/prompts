
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type LoadingType =
  | 'spinner'
  | 'dots'
  | 'ring'
  | 'ball'
  | 'bars'
  | 'infinity';
export type LoadingSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'daisy-loading',
  standalone: true,
  imports: [CommonModule],
  template: ` <span [class]="classes"></span> `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoadingComponent {
  @Input() type: LoadingType = 'spinner';
  @Input() size: LoadingSize | null = null;
  @Input() customClass = '';

  get classes(): string {
    const baseClasses = 'loading';
    const typeClass = `loading-${this.type}`;
    const sizeClass = this.size ? `loading-${this.size}` : '';

    return [baseClasses, typeClass, sizeClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }
}
