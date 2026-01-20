
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type AvatarShape = 'rounded' | 'rounded-xl' | 'rounded-full';
export type AvatarMask =
  | 'mask-squircle'
  | 'mask-heart'
  | 'mask-hexagon-2'
  | 'mask-triangle'
  | 'mask-diamond'
  | 'mask-star-2';

@Component({
  selector: 'daisy-avatar',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div [class]="containerClasses">
      <div [class]="wrapperClasses">
        @if (src) {
        <img [src]="src" [alt]="alt" />
        } @else {
        <span [class]="textClasses">{{ placeholder }}</span>
        }
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AvatarComponent {
  @Input() src: string | null = null;
  @Input() alt = '';
  @Input() size: 'w-8' | 'w-12' | 'w-16' | 'w-20' | 'w-24' | 'w-32' = 'w-24';
  @Input() shape: AvatarShape = 'rounded';
  @Input() mask: AvatarMask | null = null;
  @Input() online: boolean | null = null;
  @Input() placeholder = '';
  @Input() customClass = '';

  get containerClasses(): string {
    const baseClasses = 'avatar';
    const onlineClass =
      this.online === true
        ? 'avatar-online'
        : this.online === false
        ? 'avatar-offline'
        : '';
    const placeholderClass = this.src ? '' : 'avatar-placeholder';

    return [baseClasses, onlineClass, placeholderClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }

  get wrapperClasses(): string {
    const baseClasses = 'bg-base-300';
    const maskClass = this.mask ? this.mask : '';
    const shapeClass = this.shape ? this.shape : '';
    const sizeClass = this.size ? this.size : '';

    const result = [baseClasses, sizeClass, shapeClass, maskClass]
      .filter(Boolean)
      .join(' ');

    if (this.src) {
      return result;
    }

    return `${result} bg-neutral text-neutral-content`;
  }

  get textClasses(): string {
    switch (this.size) {
      case 'w-32':
        return 'text-5xl';
      case 'w-24':
        return 'text-3xl';
      case 'w-20':
        return 'text-2xl';
      case 'w-16':
        return 'text-xl';
      default:
        return '';
    }
  }
}
