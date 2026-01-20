
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface AccordionItem {
  title: string;
  content: string;
  checked?: boolean;
}

@Component({
  selector: 'daisy-accordion',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div [class]="'join join-vertical bg-base-100 ' + customClass">
      <div
        *ngFor="let item of items; let i = index"
        [class]="'collapse collapse-arrow join-item border-base-300 border'">
        <input
          type="radio"
          [name]="name"
          [id]="name + i"
          [checked]="item.checked" />
        <div class="collapse-title font-semibold">
          <label [for]="name + i">{{ item.title }}</label>
        </div>
        <div class="collapse-content text-sm">
          <p>{{ item.content }}</p>
        </div>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AccordionComponent {
  @Input() items: AccordionItem[] = [];
  @Input() name = 'accordion';
  @Input() customClass = '';
}
