
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type StackVerticalAlignment = 'top' | 'bottom';
export type StackHorizontalAlignment = 'start' | 'end';

@Component({
  selector: 'daisy-stack',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="stack" [class]="classes">
      <ng-content></ng-content>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class StackComponent {
  @Input() alignVertical: StackVerticalAlignment | null = null;
  @Input() alignHorizontal: StackHorizontalAlignment | null = null;
  @Input() customClass = '';

  get classes(): string {
    const verticalClass = this.alignVertical ? `stack-${this.alignVertical}` : '';
    const horizontalClass = this.alignHorizontal ? `stack-${this.alignHorizontal}` : '';

    return [verticalClass, horizontalClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }
}
