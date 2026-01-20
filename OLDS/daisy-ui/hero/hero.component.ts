
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'daisy-hero',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      class="hero rounded"
      [class]="customClass"
      [style.min-height]="minHeight"
      [style.background-image]="backgroundImage ? 'url(' + backgroundImage + ')' : ''"
    >
      @if (backgroundImage) {
      <div class="hero-overlay rounded"></div>
      }
      <div class="hero-content text-center text-neutral-content">
        <ng-content></ng-content>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HeroComponent {
  @Input() backgroundImage: string | null = null;
  @Input() minHeight = '30rem';
  @Input() customClass = '';
}
