
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

export interface BreadcrumbItem {
  label: string;
  link?: string;
}

@Component({
  selector: 'daisy-breadcrumbs',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="text-sm breadcrumbs">
      <ul>
        <li *ngFor="let item of items; let last = last">
          <a *ngIf="item.link && !last; else noLink" [routerLink]="item.link">
            {{ item.label }}
          </a>
          <ng-template #noLink>
            <span>{{ item.label }}</span>
          </ng-template>
        </li>
      </ul>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BreadcrumbsComponent {
  @Input() items: BreadcrumbItem[] = [];
}
