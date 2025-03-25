# Replication Package for Empirically Evaluating the Use of Bytecode for Diversity-Based Test Case Prioritisation

This replication package contains all necessary scripts, data, and results to reproduce the experiments from our study on the impact of bytecode diversity in test case prioritisation (TCP).

## Repository Structure

The replication package consists of the following directories:

### 1. `Scripts/`
This directory contains all Python scripts used to execute various steps of our study, including:
- **Test Subject Processing**: Scripts to preprocess test subjects for coverage and similarity calculations.
- **Similarity Calculations**: Scripts to compute similarity metrics between test cases.
- **TCP Implementations**: Scripts implementing different TCP techniques using both textual and bytecode representations.

### 2. `Resources/`
This directory contains essential data files used in our TCP approaches, including:
- **Similarity Files**: Precomputed similarity metrics for test cases.
- **Mutation Kill Maps**: Data files mapping tests to mutants.
- **Coverage Information**: Test coverage data for all test cases.
- **Error-Revealing Tests**: Identified error-revealing test cases from experiments.

### 3. `FAST-replication/`
This directory includes the implementation of **FAST-TCP**, modified to work with textual and bytecode information.

### 4. `Plots/`
This directory contains all plots generated from our experimental results.

## How to Use

To replicate the results, follow these steps:

1. **Install Dependencies**
   Ensure you have Python and necessary libraries installed. You can install the dependencies using:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run TCP Approaches**
   Execute the scripts in `Scripts/` to reproduce TCP results. 

   ## Running Coverage-Based TCP

    To execute coverage-based TCP using either **greedy total** or **greedy additional**, use the following command:

    ```bash
    python3 scripts/TCP_coverage.py [project] [True/False]
    ```

    #### Parameters:
    - **[project]**: Specify the project to analyze. Choose one of the following options:
        - `cli`
        - `compress`
        - `csv`
        - `jsoup`
        - `lang`
        - `math`
        - `time`
    - **[True/False]**: 
        - Use `True` for **Total Coverage** (greedy total).
        - Use `False` for **Additional Coverage** (greedy additional).

    #### Example:
    To run **greedy total** on the `math` project:
    ```bash
    python3 scripts/TCP_coverage.py math True
    ```

    To run **greedy additional** on the `jsoup` project:
    ```bash
    python3 scripts/TCP_coverage.py jsoup False
    ```

    ## Running Ledru-TCP

    To run Ledru-TCP using textual information.

    ```bash
    python3 scripts/TCP_text.py [project]
    ```
    
    To run Ledru-TCP using bytecode information.
    ```bash
    python3 scripts/TCP_bytecode.py [project]
    ```

    ## Running FAST-TCP

    To run FAST-TCP using text or bytecode information.
    ```bash
    python3 scripts/TCP_FAST.py [project] [artefact]
    ```
    
    #### Parameters:
    - **[artefact]**: Specify the used artefact. Choose one of the following options:
        - `text`
        - `bytecode`

3. **Reproducing FAST-TCP Results**
   Navigate to `FAST-replication/` and follow the instructions in its README to run FAST-TCP experiments.

<!-- ## Citation
If you use this replication package, please cite our paper:
```
[Provide citation information here]
```

## Contact
For any issues or questions, please contact [Your Email/Contact Information]. -->

