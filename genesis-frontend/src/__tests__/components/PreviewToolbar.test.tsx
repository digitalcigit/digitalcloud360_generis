import { describe, expect, it, jest } from '@jest/globals';
import { fireEvent, render } from '@testing-library/react';
import PreviewToolbar from '@/components/PreviewToolbar';

describe('PreviewToolbar', () => {
    it('calls onViewportChange when viewport buttons are clicked', () => {
        const onViewportChange = jest.fn();

        const { getByLabelText } = render(
            <PreviewToolbar currentViewport="desktop" onViewportChange={onViewportChange} />
        );

        fireEvent.click(getByLabelText('Viewport mobile'));
        expect(onViewportChange).toHaveBeenCalledWith('mobile');

        fireEvent.click(getByLabelText('Viewport tablette'));
        expect(onViewportChange).toHaveBeenCalledWith('tablet');

        fireEvent.click(getByLabelText('Viewport desktop'));
        expect(onViewportChange).toHaveBeenCalledWith('desktop');
    });

    it('disables actions when handlers are missing', () => {
        const { getByLabelText } = render(
            <PreviewToolbar currentViewport="desktop" onViewportChange={() => undefined} />
        );

        expect((getByLabelText('Retour au chat') as HTMLButtonElement).disabled).toBe(true);
        expect((getByLabelText('Plein écran') as HTMLButtonElement).disabled).toBe(true);
    });

    it('calls onBack and onFullscreen when clicked', () => {
        const onBack = jest.fn();
        const onFullscreen = jest.fn();

        const { getByLabelText } = render(
            <PreviewToolbar
                currentViewport="desktop"
                onViewportChange={() => undefined}
                onBack={onBack}
                onFullscreen={onFullscreen}
            />
        );

        fireEvent.click(getByLabelText('Retour au chat'));
        expect(onBack).toHaveBeenCalledTimes(1);

        fireEvent.click(getByLabelText('Plein écran'));
        expect(onFullscreen).toHaveBeenCalledTimes(1);
    });
});
