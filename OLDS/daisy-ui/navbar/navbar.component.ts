
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'daisy-navbar',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="navbar" [class]="customClass">
      <div class="navbar-start">
        <ng-content select="[navbar-start]"></ng-content>
      </div>
      <div class="navbar-center">
        <ng-content select="[navbar-center]"></ng-content>
      </div>
      <div class="navbar-end">
        <ng-content select="[navbar-end]"></ng-content>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NavbarComponent {
  @Input() customClass = '';
}
