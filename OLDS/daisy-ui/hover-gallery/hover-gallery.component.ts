
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'daisy-hover-gallery',
  standalone: true,
  imports: [CommonModule],
  template: `
    <figure class="hover-gallery" [class]="customClass">
      @for (imageSrc of images; track $index) {
      <img [src]="imageSrc" alt="Gallery image" />
      }
    </figure>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HoverGalleryComponent {
  @Input() images: string[] = [];
  @Input() customClass = '';
}
