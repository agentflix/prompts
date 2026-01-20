
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type SkeletonShape = 'square' | 'circle' | 'text';

@Component({
  selector: 'daisy-skeleton',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      class="skeleton"
      [class]="classes"
      [style.width]="width"
      [style.height]="height"
    ></div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SkeletonComponent {
  @Input() width: string | null = null; // e.g., '32px', 'w-full'
  @Input() height: string | null = null; // e.g., '32px', 'h-4'
  @Input() shape: SkeletonShape = 'square'; // 'square', 'circle', 'text'
  @Input() customClass = '';

  get classes(): string {
    const shapeClass = this.shape === 'circle' ? 'rounded-full' : '';
    const textClass = this.shape === 'text' ? 'h-4 w-full' : ''; // Default text line style

    return [shapeClass, textClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }
}
