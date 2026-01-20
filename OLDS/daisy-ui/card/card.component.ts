
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type CardStyle = 'border' | 'dash';
export type CardSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'daisy-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div [class]="classes">
      <ng-content select="[card-figure]"></ng-content>
      <div class="card-body">
        <ng-content select="[card-title]"></ng-content>
        <ng-content></ng-content>
        <ng-content select="[card-actions]"></ng-content>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CardComponent {
  @Input() style: CardStyle | null = null;
  @Input() size: CardSize | null = null;
  @Input() side: 'side' | 'responsive' | null = null;
  @Input() imageFull = false;
  @Input() customClass = '';

  get classes(): string {
    const baseClasses = 'card w-96 bg-base-100 shadow-sm';
    const styleClass = this.style ? `card-${this.style}` : '';
    const sizeClass = this.size ? `card-${this.size}` : '';
    const sideClass =
      this.side === 'side'
        ? 'card-side'
        : this.side === 'responsive'
        ? 'lg:card-side'
        : '';
    const imageFullClass = this.imageFull ? 'image-full' : '';

    return [
      baseClasses,
      styleClass,
      sizeClass,
      sideClass,
      imageFullClass,
      this.customClass,
    ]
      .filter(Boolean)
      .join(' ');
  }
}
