using CP;

tuple Objective {
	int task_id;
	float coefficient;
}

tuple Task {
	key int id;
	int length; 
}

tuple Resource {
	int id;
    	int capacity_low;
    	int capacity_up;
}

tuple PulseResource {
	key int id;
	int resource_size;
}

tuple TaskPulseResource {
	key int task_id;
	key int pulse_resource_id;
	int resource_size_req;
}

tuple TaskResource {
	int task_id;
	int resource_id;
	int length;
	int group_id;
}

// one group for every task-alternative
tuple TaskResourceGroup {
  	int task_id;
  	int group_id;
}

tuple Precedence {
	int left_task;
	int right_task;
	float offset;
}

tuple CondPrecedence {
	int left_task;
	int right_task;
	int offset;
}

tuple Bound {
	int task;
	float bound;
}


{Objective} Objectives = ...;
{Task} Tasks = ...;
{Resource} Resources = ...;
{PulseResource} PulseResources = ...;
{TaskPulseResource} TaskPulseResources = ...;
{TaskResource} TaskResources = ...;
{TaskResourceGroup} TaskResourceGroups = ...;
{Precedence} Precedences = ...;
{Precedence} TightPrecedences = ...;
{CondPrecedence} CondPrecedences = ...;
{Bound} UpperBounds = ...;
{Bound} LowerBounds = ...;
{Bound} FixBounds = ...;



dvar interval Intervals[ T in Tasks ] size T.length;
dvar interval RIntervals[ TR in TaskResources ] optional size TR.length;

dvar sequence Resource_Seq[R in Resources] in all(TR in TaskResources : TR.resource_id == R.id) RIntervals[TR] types all(TR in TaskResources  : TR.resource_id == R.id) TR.task_id;

cumulFunction ResourceFunction[TPR in TaskPulseResources] = pulse(Intervals[<TPR.task_id>],TPR.resource_size_req) ;


execute { cp.param.FailLimit = 1000000; }


minimize sum(T in Tasks ) sum( O in Objectives : O.task_id == T.id ) endOf(Intervals[T]) * O.coefficient;

subject to {

  forall (R in Resources)
  {
	   noOverlap(Resource_Seq[R],CondPrecedences);  
  }  

  forall( R in Resources )
  {
  	sum(TR in TaskResources) presenceOf(RIntervals[TR]) <= R.capacity_up;
  	sum(TR in TaskResources) presenceOf(RIntervals[TR]) >= R.capacity_low;
  } 

  forall (P in Precedences)
  {
     endOf(Intervals[ item(Tasks,P.left_task) ]) + P.offset <= startOf(Intervals[ item(Tasks,P.right_task) ]) ;
  }

  forall (P in TightPrecedences)
  {
     endOf(Intervals[ item(Tasks,P.left_task) ]) + P.offset == startOf(Intervals[ item(Tasks,P.right_task) ]) ;
     //endOf(Intervals[ item(Tasks,P.left_task) ]) + P.offset >= startOf(Intervals[ item(Tasks,P.right_task) ]) ;
  }
  
  forall (B in UpperBounds)
  {
     endOf(Intervals[ item(Tasks,B.task) ]) <= B.bound;    
  }
  
  forall (B in LowerBounds)
  {
     startOf(Intervals[ item(Tasks,B.task) ]) >= B.bound;    
  }

  forall (B in FixBounds)
  {
     startOf(Intervals[ item(Tasks,B.task) ]) == B.bound;    
  }
  
  forall(T in Tasks){
        forall( TRG in TaskResourceGroups : TRG.task_id == T.id ){
               		alternative(Intervals[T], all(TR in TaskResources : ( TR.group_id == TRG.group_id ) && ( TR.task_id == T.id ) ) RIntervals[TR]); // Resource Selection        
        }
  }
  
  forall( PR in PulseResources ){
             sum( TPR in TaskPulseResources : TPR.pulse_resource_id == PR.id ) ResourceFunction[TPR] <= PR.resource_size; 
  }

};

execute {
	//var f = new IloOplOutputFile(##out_filename##);//"tmp/cpoptimizer.out");
	write("##START_INTERVALS##")	
	for ( TR in TaskResources)
	{
		//f.write(TR.task_id," ",TR.resource_id);f.writeln(RIntervals[TR]);
		write(TR.task_id," ",TR.resource_id);write(RIntervals[TR]);
	}
	write("##END_INTERVALS##")	
}




