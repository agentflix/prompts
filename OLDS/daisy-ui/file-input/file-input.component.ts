
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

export type FileInputColor =
  | 'neutral'
  | 'primary'
  | 'secondary'
  | 'accent'
  | 'info'
  | 'success'
  | 'warning'
  | 'error';
export type FileInputSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'daisy-file-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <input
      type="file"
      [class]="classes"
      [disabled]="disabled"
      [placeholder]="placeholder"
      (change)="onFileChange($event)"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FileInputComponent {
  @Input() color: FileInputColor | null = null;
  @Input() size: FileInputSize | null = null;
  @Input() ghost = false;
  @Input() disabled = false;
  @Input() placeholder = '';
  @Input() customClass = '';

  @Output() fileChange = new EventEmitter<FileList | null>();

  get classes(): string {
    const baseClasses = 'file-input';
    const colorClass = this.color ? `file-input-${this.color}` : '';
    const sizeClass = this.size ? `file-input-${this.size}` : '';
    const ghostClass = this.ghost ? 'file-input-ghost' : '';

    return [
      baseClasses,
      colorClass,
      sizeClass,
      ghostClass,
      this.customClass,
    ]
      .filter(Boolean)
      .join(' ');
  }

  onFileChange(event: Event): void {
    const files = (event.target as HTMLInputElement).files;
    this.fileChange.emit(files);
  }
}
