
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'daisy-diff',
  standalone: true,
  imports: [CommonModule],
  template: `
    <figure class="diff rounded-field aspect-16/9" tabindex="0" [class]="customClass">
      <div class="diff-item-1" role="img" tabindex="0">
        <ng-content select="[diff-item-1]"></ng-content>
      </div>
      <div class="diff-item-2" role="img">
        <ng-content select="[diff-item-2]"></ng-content>
      </div>
      <div class="diff-resizer"></div>
    </figure>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DiffComponent {
  @Input() customClass = '';
}
