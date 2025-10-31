
#from simulation import run_simulation
# main.py

from simulation import run_batch_simulation

if __name__ == "__main__":
    # Altere o número de batches para 100 após o teste inicial
    run_batch_simulation(num_batches=10) 
    # A função run_simulation retornará o GIF para exibição no Colab
    #Teste Unitario
    #gif = run_simulation() 
    #if gif:
    #    from IPython.display import display
    #    display(gif)
