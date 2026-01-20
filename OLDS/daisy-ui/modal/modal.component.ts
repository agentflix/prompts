
import { ChangeDetectionStrategy, Component, Input, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';

export type ModalPlacement = 'top' | 'middle' | 'bottom' | 'start' | 'end';

@Component({
  selector: 'daisy-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <dialog #modalElement [id]="id" class="modal" [class]="classes">
      <div class="modal-box" [class]="modalBoxCustomClass">
        <ng-content select="[modal-content]"></ng-content>
        <div class="modal-action">
          <form method="dialog">
            <ng-content select="[modal-actions]"></ng-content>
          </form>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" [class]="modalBackdropCustomClass">
        <ng-content select="[modal-backdrop-content]"></ng-content>
      </form>
    </dialog>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ModalComponent implements AfterViewInit {
  @Input() id!: string;
  @Input() open = false;
  @Input() placement: ModalPlacement[] = [];
  @Input() customClass = '';
  @Input() modalBoxCustomClass = '';
  @Input() modalBackdropCustomClass = '';

  @ViewChild('modalElement') modalElement!: ElementRef<HTMLDialogElement>;

  ngAfterViewInit(): void {
    if (this.open) {
      this.modalElement.nativeElement.showModal();
    }
  }

  get classes(): string {
    const placementClasses = this.placement.map((p) => `modal-${p}`).join(' ');
    return [placementClasses, this.customClass].filter(Boolean).join(' ');
  }

  showModal(): void {
    this.modalElement.nativeElement.showModal();
  }

  closeModal(): void {
    this.modalElement.nativeElement.close();
  }
}
