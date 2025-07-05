# FDGNode Parameter Documentation

This document provides a detailed explanation of each parameter available in the `FDGNode` from the ComfyUI-FDG extension. Understanding these parameters will help you fine-tune the image generation process to achieve desired artistic effects and image quality.

The FDGNode implements the techniques described in the paper "[Guidance in the Frequency Domain Enables High-Fidelity Sampling at Low CFG Scales](https://arxiv.org/abs/2506.19713)". It allows for applying different guidance strengths and characteristics across various frequency bands of an image during generation.

## Parameters

Below are the parameters for the `FDGNode`, which can be found in the `advanced/model` category in ComfyUI.

### `model`
-   **Type**: `MODEL`
-   **Purpose**: This is the input generative model that will be patched by the FDGNode.
-   **Practical Use**: Connect the output of a model loader (e.g., Load Checkpoint) to this input. The FDGNode will then apply its frequency-decoupled guidance logic to this model during the sampling process.
-   **Effect**: The original model's behavior is modified to use the FDG guidance strategy instead of (or in combination with, depending on `fdg_steps`) standard CFG.

### `guidance_scale_high`
-   **Type**: `FLOAT`
-   **Default**: `7.5`
-   **Range**: `0.0` to `100.0` (step `0.1`)
-   **Purpose**: Sets the guidance strength for the highest frequency components of the image. High frequencies correspond to fine details, textures, and sharp edges.
-   **Practical Use**:
    -   Higher values (e.g., 5-15) will make the fine details adhere more strongly to the prompt. This can lead to sharper, more detailed images but might also introduce noise or artifacts if set too high.
    -   Lower values (e.g., 1-3) will result in softer details and a less strict adherence to the prompt at the fine level.
    -   If `levels` is set to 1, this single `guidance_scale_high` value is applied across all frequencies.
-   **Effect**: Directly influences the sharpness and prominence of fine textures and details. A higher value here can make images appear crisper.

### `guidance_scale_low`
-   **Type**: `FLOAT`
-   **Default**: `1.0`
-   **Range**: `0.0` to `100.0` (step `0.1`)
-   **Purpose**: Sets the guidance strength for the lowest frequency components of the image. Low frequencies correspond to the overall composition, global shapes, and broad color distributions.
-   **Practical Use**:
    -   Higher values will make the overall composition and larger forms adhere more strongly to the prompt.
    -   Lower values allow the model more freedom in interpreting the broader aspects of the prompt, potentially leading to more creative or varied compositions. Values around 1.0-2.0 are common for allowing creative freedom while maintaining coherence.
    -   The FDG paper suggests that low CFG scales are beneficial for overall image quality, and this parameter allows you to control the guidance for these crucial low-frequency components.
-   **Effect**: Affects the global structure and composition. Higher values ensure the main subjects and layout follow the prompt closely. Lower values can lead to more dream-like or abstract structures.

### `levels`
-   **Type**: `INT`
-   **Default**: `3`
-   **Range**: `1` to `8` (step `1`)
-   **Purpose**: Determines the number of frequency bands (pyramid levels) the image is decomposed into for applying differential guidance.
-   **Practical Use**:
    -   `1 level`: FDG is still active. In this case, `guidance_scale_high` and `parallel_weight_high` are used as the single guidance scale and parallel weight for all frequencies, respectively. The `guidance_scale_low` and `parallel_weight_low` parameters, along with interpolation settings, are effectively ignored.
    -   `2 levels`: The image is conceptually split into high and low frequencies. `guidance_scale_high` & `parallel_weight_high` apply to the high-frequency band, and `guidance_scale_low` & `parallel_weight_low` apply to the low-frequency band. Interpolation methods are not strictly active as there's no intermediate level.
    -   `3+ levels`: Allows for a smoother or more complex transition of guidance strength and parallel weights from high to low frequencies, as defined by the `scale_interpolation` and `weight_interpolation` methods. More levels provide finer control over mid-frequency bands where these interpolations take effect.
-   **Effect**:
    -   More levels allow for more nuanced control over how guidance changes from fine details to coarse structures.
    -   Increasing levels also slightly increases computational cost due to the Laplacian pyramid decomposition and reconstruction.
    -   The choice of `levels` interacts significantly with the interpolation modes. With more levels, the chosen interpolation curve has more points to shape the guidance transition.

### `scale_interpolation`
-   **Type**: `ENUM` (Options: `linear`, `cosine`, `quadratic_ease_in`, `quadratic_ease_out`, `step`)
-   **Default**: `linear`
-   **Purpose**: Defines how the guidance scale transitions from `guidance_scale_high` to `guidance_scale_low` across the specified `levels`.
-   **Practical Use & Effect**:
    -   `linear`: Provides a straight, even transition. If `levels` is 3, and scales are 7.0 (high) and 1.0 (low), the intermediate level would be at 4.0. This is a good general-purpose default.
        -   *Effect*: Smooth, predictable change in guidance from fine details to coarse structures.
    -   `cosine`: Uses a cosine curve for interpolation, resulting in smoother easing at the start and end of the transition.
        -   *Effect*: Can provide a more organic or natural-feeling transition in detail emphasis.
    -   `quadratic_ease_in`: The transition starts slowly from `guidance_scale_high` and accelerates towards `guidance_scale_low`. This means higher frequencies (details) retain stronger guidance for more of the pyramid levels, while lower frequencies quickly adopt `guidance_scale_low`.
        -   *Effect*: Emphasizes prompt adherence in finer details more strongly across more frequency bands.
    -   `quadratic_ease_out`: The transition starts quickly from `guidance_scale_high` and decelerates towards `guidance_scale_low`. High frequencies rapidly transition away from `guidance_scale_high`, while lower frequencies maintain values closer to `guidance_scale_high` for more levels before they, too, transition towards `guidance_scale_low`.
        -   *Effect*: Can be used if you want strong initial guidance on details but want the mid and low frequencies to also be strongly guided before tapering off to `guidance_scale_low`.
    -   `step`: Applies `guidance_scale_high` to the first half of the frequency levels (higher frequencies) and `guidance_scale_low` to the second half (lower frequencies).
        -   If the number of `levels` is odd, the middle level receives `guidance_scale_high`.
        -   *Effect*: Creates a more abrupt, binary shift in guidance strategy between higher and lower frequencies, rather than a gradual transition. Useful for a distinct separation of how details and structures are guided.

### `parallel_weight_high`
-   **Type**: `FLOAT`
-   **Default**: `1.0`
-   **Range**: `0.0` to `2.0` (step `0.05`)
-   **Purpose**: Modulates the strength of the "parallel component" of the guidance signal for the highest frequency components (fine details). The guidance signal (difference between conditional and unconditional predictions) is decomposed into two parts: one parallel to the conditional prediction (related to style, intensity) and one orthogonal to it (related to semantic content, structure).
-   **Practical Use**:
    -   `1.0`: Uses the parallel component as is. This is the standard behavior in many guidance implementations.
    -   `> 1.0`: Amplifies the parallel component. This can enhance stylistic elements, contrast, or intensity of details that align with the conditional model's tendencies. Might lead to over-saturation or exaggerated features if too high.
    -   `< 1.0`: Dampens the parallel component. This relatively increases the influence of the orthogonal component, potentially leading to more "structural" or "semantic" guidance for details, rather than stylistic emphasis.
    -   `0.0`: Completely removes the parallel component for high frequencies, using only the orthogonal part of the guidance. This might result in a unique, perhaps flatter or more abstract, rendering of details.
-   **Effect**: Affects the character of fine details. Higher values can make details "pop" more or appear more intense/stylized. Lower values can make details more subtle or emphasize their form over their intensity.

### `parallel_weight_low`
-   **Type**: `FLOAT`
-   **Default**: `1.0`
-   **Range**: `0.0` to `2.0` (step `0.05`)
-   **Purpose**: Similar to `parallel_weight_high`, but applies to the lowest frequency components (overall composition and broad structures).
-   **Practical Use**:
    -   `1.0`: Standard weighting for the parallel component in coarse structures.
    -   `> 1.0`: Can make the overall image appear more contrasted or stylistically strong in its basic forms.
    -   `< 1.0`: May lead to a softer overall composition, where structural guidance (orthogonal) is more dominant than stylistic (parallel) guidance for large forms.
    -   `0.0`: Uses only orthogonal guidance for the main composition.
-   **Effect**: Influences the global contrast and stylistic rendering of the image's foundational elements.

### `weight_interpolation`
-   **Type**: `ENUM` (Options: `linear`, `cosine`, `quadratic_ease_in`, `quadratic_ease_out`, `step`)
-   **Default**: `linear`
-   **Purpose**: Defines how the parallel weight transitions from `parallel_weight_high` to `parallel_weight_low` across the specified `levels`.
-   **Practical Use & Effect**: The interpolation methods behave analogously to `scale_interpolation`, but they control the transition of the parallel component's weight.
    -   `linear`: Smooth, even transition of parallel weight.
    -   `cosine`: Smoother easing for parallel weight transition.
    -   `quadratic_ease_in`: Parallel weight stays closer to `parallel_weight_high` for more levels, then quickly shifts to `parallel_weight_low`.
    -   `quadratic_ease_out`: Parallel weight quickly shifts from `parallel_weight_high` and then slowly approaches `parallel_weight_low`.
    -   `step`: Abrupt change in parallel weighting strategy between high and low frequencies.
    -   This allows fine-tuning of how stylistic aspects (influenced by parallel weights) are emphasized across different frequency bands. For example, one might want strong parallel weighting for details (high frequencies) but less for overall structure (low frequencies), or vice-versa.

### `fdg_steps`
-   **Type**: `INT`
-   **Default**: `2`
-   **Min**: `0`
-   **Max**: `1000` (step `1`)
-   **Purpose**: Specifies the number of initial sampling steps during which FDG (Frequency Decoupled Guidance) is applied. After these steps, the sampler switches to standard Classifier-Free Guidance (CFG) using the CFG value set in the KSampler node.
-   **Practical Use**:
    -   The FDG paper often applies its method for only the initial steps of the diffusion process, as these steps are crucial for establishing the image structure.
    -   `0`: FDG is effectively disabled. The model is still patched, but the internal logic will use standard CFG for all steps. The KSampler's CFG value will be used. (Note: if KSampler CFG is 1.0, `guidance_scale_high` from this node is used instead due to a specific behavior in `fdg_function`).
    -   `Small value (e.g., 1-5)`: FDG is used for the very early, formative stages of image generation. This can help establish good low-frequency structure with low effective CFG scales, then standard CFG takes over for refinement.
    -   `Moderate to high value (e.g., >5 up to total sampler steps)`: FDG is applied for a larger portion or all of the sampling process. If `fdg_steps` is greater than or equal to the total number of steps in the KSampler, FDG will be used throughout.
    -   The actual switch from FDG to standard CFG is based on comparing the current sigma value in the sampling process to a threshold derived from `fdg_steps` and the sampler's sigma schedule.
-   **Effect**:
    -   Controls the "duration" of FDG's influence. Applying FDG for a few initial steps can give the benefits of low-CFG structural generation while allowing later steps to refine details with standard CFG.
    -   Using FDG for all steps means the entire generation process is governed by the frequency-specific guidance parameters.
    -   Setting to 0 provides a way to easily switch off FDG without removing/bypassing the node, allowing for A/B testing. The KSampler's CFG value becomes dominant.
    -   **Important Interaction with KSampler CFG**: When FDG is active (i.e., current step is within `fdg_steps`), the `guidance_scale_high` to `guidance_scale_low` settings dictate the guidance. When `fdg_steps` are exceeded and the system switches to standard CFG, the CFG value from the KSampler node is used. However, there's a nuance: if the KSampler's CFG is set to `1.0` AND `fdg_steps` are exceeded (or `fdg_steps` is 0), the `fdg_function` uses `guidance_scale_high` as the CFG scale. This is an edge case to be aware of. For typical CFG values (e.g., 7.0) in the KSampler, that value will be used when FDG is not active.
