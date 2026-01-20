
# Modal Component

This component displays a dialog or a box, utilizing the native HTML `<dialog>` element for accessibility and functionality.

## Usage

```html
<daisy-modal id="my_modal" [open]="isModalOpen">
  <div modal-content>
    <h3 class="font-bold text-lg">Hello!</h3>
    <p class="py-4">Press ESC key or click the button below to close</p>
  </div>
  <div modal-actions>
    <button class="btn">Close</button>
  </div>
</daisy-modal>
```

## Inputs

- `id`: `string` - A unique ID for the modal. This is required for the native `<dialog>` element.
- `open`: `boolean` - Controls whether the modal is initially open.
- `placement`: `ModalPlacement[]` - An array of strings to control the placement of the modal. Can include `top`, `middle`, `bottom`, `start`, `end`.
- `customClass`: `string` - Custom classes to add to the modal container.
- `modalBoxCustomClass`: `string` - Custom classes to add to the `modal-box` element.
- `modalBackdropCustomClass`: `string` - Custom classes to add to the `modal-backdrop` element.

## Methods

- `showModal()`: Opens the modal.
- `closeModal()`: Closes the modal.

## Content Projection

The modal component uses content projection for its various parts:

- `[modal-content]`: Use this attribute on an element to define the main content of the modal.
- `[modal-actions]`: Use this attribute on an element to define the action buttons (e.g., close button) of the modal.
- `[modal-backdrop-content]`: Use this attribute on an element to define content for the modal backdrop (e.g., a close button that closes the modal when clicking outside).

## Example

```typescript
import { Component, ViewChild } from '@angular/core';
import { ModalComponent } from './daisy-ui/modal/modal.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ModalComponent],
  template: `
    <button class="btn" (click)="modal.showModal()">Open Modal</button>

    <daisy-modal id="my_modal_example" [placement]="['middle', 'center']" #modal>
      <div modal-content>
        <h3 class="font-bold text-lg">Hello!</h3>
        <p class="py-4">This is a modal example using the native dialog element.</p>
      </div>
      <div modal-actions>
        <button class="btn" (click)="modal.closeModal()">Close</button>
      </div>
      <div modal-backdrop-content>
        <button>close</button>
      </div>
    </daisy-modal>
  `,
})
export class AppComponent {
  @ViewChild('modal') modal!: ModalComponent;
}
```
