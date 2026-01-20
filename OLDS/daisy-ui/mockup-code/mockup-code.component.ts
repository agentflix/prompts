
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface CodeLine {
  code: string;
  prefix?: string;
  class?: string;
}

@Component({
  selector: 'daisy-mockup-code',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="mockup-code w-full" [class]="customClass">
      @for (line of codeLines; track $index) {
      <pre [attr.data-prefix]="line.prefix" [class]="line.class"><code>{{ line.code }}</code></pre>
      }
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MockupCodeComponent {
  @Input() codeLines: CodeLine[] = [];
  @Input() customClass = '';
}
