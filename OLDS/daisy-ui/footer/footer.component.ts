
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type FooterDirection = 'horizontal' | 'vertical';

@Component({
  selector: 'daisy-footer',
  standalone: true,
  imports: [CommonModule],
  template: `
    <footer [class]="classes">
      <ng-content></ng-content>
    </footer>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FooterComponent {
  @Input() direction: FooterDirection | null = null;
  @Input() center = false;
  @Input() customClass = '';

  get classes(): string {
    const baseClasses = 'footer p-10';
    const directionClass = this.direction ? `sm:footer-${this.direction}` : '';
    const centerClass = this.center ? 'footer-center' : '';

    return [baseClasses, directionClass, centerClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }
}

@Component({
  selector: 'daisy-footer-title',
  standalone: true,
  imports: [CommonModule],
  template: ` <h6 class="footer-title"><ng-content></ng-content></h6> `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FooterTitleComponent {}
