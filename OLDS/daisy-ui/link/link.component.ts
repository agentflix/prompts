
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type LinkColor =
  | 'neutral'
  | 'primary'
  | 'secondary'
  | 'accent'
  | 'success'
  | 'info'
  | 'warning'
  | 'error';

@Component({
  selector: 'a[daisy-link], button[daisy-link]',
  standalone: true,
  imports: [CommonModule],
  template: ` <ng-content></ng-content> `,
  host: {
    '[class]': 'classes',
  },
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LinkComponent {
  @Input() color: LinkColor | null = null;
  @Input() hover = false;
  @Input() customClass = '';

  get classes(): string {
    const baseClasses = 'link';
    const colorClass = this.color ? `link-${this.color}` : '';
    const hoverClass = this.hover ? 'link-hover' : '';

    return [baseClasses, colorClass, hoverClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }
}
