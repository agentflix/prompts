
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type KbdSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'daisy-kbd',
  standalone: true,
  imports: [CommonModule],
  template: `
    <kbd [class]="classes">
      <ng-content></ng-content>
    </kbd>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class KbdComponent {
  @Input() size: KbdSize | null = null;
  @Input() customClass = '';

  get classes(): string {
    const baseClasses = 'kbd';
    const sizeClass = this.size ? `kbd-${this.size}` : '';

    return [baseClasses, sizeClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }
}
