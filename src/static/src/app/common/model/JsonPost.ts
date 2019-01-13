export class JsonPost {

  public module: string; 
  public method: string;  
  public parameters: Array<any> = new Array<any>()  

  constructor(module, method, parameters?){
      this.module = module;
      this.method = method;
      this.parameters = parameters;
  }   
} 

/*{
	"module":"devicesService",
	"parameters":[],
	"method":"loadDevives"
}*/