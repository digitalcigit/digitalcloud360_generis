import { test, expect } from './fixtures/auth';
import { CoachingStepEnum } from '../src/types/coaching';

/**
 * E2E Tests: Coaching Interface (Silver Level)
 * GEN-WO-003: Proactive coaching flow validation
 */

test.describe('Coaching Interface', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    // Mock Start Session
    await authenticatedPage.route('**/api/coaching/start', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          session_id: "test-session-123",
          current_step: "vision",
          coach_message: "Bienvenue ! Parlons de votre vision.",
          examples: ["Exemple 1", "Exemple 2"],
          progress: { vision: false, mission: false, clientele: false, differentiation: false, offre: false },
          is_step_complete: false,
          clickable_choices: [{ id: "c1", text: "Choix 1" }]
        })
      });
    });

    // Mock Step (Generic success)
    await authenticatedPage.route('**/api/coaching/step', async (route) => {
        const body = await route.request().postDataJSON();
        // Simulate progression based on input or just success
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
                session_id: "test-session-123",
                current_step: "mission", // Move to next step
                coach_message: "Super vision ! Maintenant la mission.",
                examples: [],
                progress: { vision: true, mission: false, clientele: false, differentiation: false, offre: false },
                is_step_complete: true,
                clickable_choices: []
            })
        });
    });

    // Mock Help
    await authenticatedPage.route('**/api/coaching/help', async (route) => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
                session_id: "test-session-123",
                current_step: "vision",
                socratic_questions: [
                    { 
                        question: "Pourquoi faites-vous cela ?", 
                        context_hint: "Pensez à votre motivation",
                        choices: [{id: "r1", text: "Pour l'argent"}, {id: "r2", text: "Pour la passion"}]
                    }
                ],
                suggestion: "Essayez de vous concentrer sur le 'Pourquoi'."
            })
        });
    });

    // Mock Proposals ("I don't know")
    await authenticatedPage.route('**/api/coaching/generate-proposals', async (route) => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
                session_id: "test-session-123",
                step: "vision",
                proposals: [
                    { id: "p1", title: "Proposition 1", content: "Contenu prop 1", justification: "Car c'est bien" },
                    { id: "p2", title: "Proposition 2", content: "Contenu prop 2", justification: "Car c'est mieux" },
                    { id: "p3", title: "Proposition 3", content: "Contenu prop 3", justification: "Car c'est top" }
                ],
                coach_advice: "Choisissez ce qui vous parle le plus."
            })
        });
    });

    // Mock Reformulate
    await authenticatedPage.route('**/api/coaching/reformulate', async (route) => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
                original_text: "text",
                reformulated_text: "Texte reformulé professionnellement.",
                is_better: true,
                suggestions: []
            })
        });
    });

    await authenticatedPage.goto('/coaching');
    // Wait for the page to load and API to respond
    await authenticatedPage.waitForLoadState('networkidle');
  });

  test('should display initial coaching state correctly', async ({ authenticatedPage }) => {
    // Check Header
    await expect(authenticatedPage.getByText('Coach Genesis AI')).toBeVisible();
    await expect(authenticatedPage.getByText('Mode Maïeutique Argent')).toBeVisible();

    // Check Coach Message
    await expect(authenticatedPage.getByText('Bienvenue ! Parlons de votre vision.')).toBeVisible();

    // Check Input area
    await expect(authenticatedPage.getByTestId('chat-input')).toBeVisible();
  });

  test('should allow sending a message via text input', async ({ authenticatedPage }) => {
    const input = authenticatedPage.getByTestId('chat-input');
    const sendButton = authenticatedPage.getByTestId('send-btn');

    await input.fill('Ma vision est de changer le monde.');
    await expect(sendButton).toBeEnabled();
    
    await sendButton.click();

    // Should receive response moving to Mission
    await expect(authenticatedPage.getByText('Super vision ! Maintenant la mission.')).toBeVisible();
  });

  test('should open Socratic Help modal', async ({ authenticatedPage }) => {
    const helpButton = authenticatedPage.getByTestId('help-btn');
    await helpButton.click();

    // Modal should appear
    await expect(authenticatedPage.getByTestId('socratic-help-modal')).toBeVisible();
    await expect(authenticatedPage.getByTestId('socratic-question-text')).toHaveText('Pourquoi faites-vous cela ?');
    
    // Close modal
    await authenticatedPage.getByTestId('skip-help-btn').click();
    await expect(authenticatedPage.getByTestId('socratic-help-modal')).toBeHidden();
  });

  test('should open Proposals modal (I dont know)', async ({ authenticatedPage }) => {
    const dkButton = authenticatedPage.getByTestId('dont-know-btn');
    await dkButton.click();

    // Modal should appear
    await expect(authenticatedPage.getByTestId('proposals-modal')).toBeVisible();
    await expect(authenticatedPage.getByTestId('proposal-card-p1')).toBeVisible();
    
    // Select a proposal (should submit and close)
    await authenticatedPage.getByTestId('proposal-card-p1').click();
    
    // Should have submitted and moved to next step (mocked response)
    await expect(authenticatedPage.getByText('Super vision ! Maintenant la mission.')).toBeVisible();
    await expect(authenticatedPage.getByTestId('proposals-modal')).toBeHidden();
  });

  test('should show clickable choices', async ({ authenticatedPage }) => {
    await expect(authenticatedPage.getByTestId('clickable-choice-c1')).toBeVisible();
    
    // Click choice
    await authenticatedPage.getByTestId('clickable-choice-c1').click();
    
    // Should submit
    await expect(authenticatedPage.getByText('Super vision ! Maintenant la mission.')).toBeVisible();
  });
});
