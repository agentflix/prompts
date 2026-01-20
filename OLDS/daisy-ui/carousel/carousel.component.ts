
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type CarouselSnap = 'start' | 'center' | 'end';
export type CarouselDirection = 'horizontal' | 'vertical';

@Component({
  selector: 'daisy-carousel',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div [class]="classes">
      <ng-content></ng-content>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CarouselComponent {
  @Input() snap: CarouselSnap = 'start';
  @Input() direction: CarouselDirection = 'horizontal';
  @Input() customClass = '';

  get classes(): string {
    const baseClasses = 'carousel rounded-box';
    const snapClass = this.snap ? `carousel-${this.snap}` : '';
    const directionClass = this.direction ? `carousel-${this.direction}` : '';

    return [baseClasses, snapClass, directionClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }
}

@Component({
  selector: 'daisy-carousel-item',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="carousel-item">
      <ng-content></ng-content>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CarouselItemComponent {}
