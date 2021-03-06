import keras
import keras.backend as K
import tensorflow as tf
from keras.models import load_model
import uff
from wide_resnet import wide_resnet
from tensorflow.python.framework import graph_io
from tensorflow.python.tools import freeze_graph
from tensorflow.core.protobuf import saver_pb2
from tensorflow.python.training import saver as saver_lib


def convert_keras_to_pb(keras_model, out_names, models_dir, model_filename):
	model = load_model(keras_model)
	out_names = model.outputs
	print(out_names)
	model.summary()
	K.set_learning_phase(0)
	sess = K.get_session()
	saver = saver_lib.Saver(write_version=saver_pb2.SaverDef.V2)
	checkpoint_path = saver.save(sess, 'saved_ckpt', global_step=0, latest_filename='checkpoint_state')
	graph_io.write_graph(sess.graph, '.', 'tmp.pb')
	freeze_graph.freeze_graph('./tmp.pb', '',
                          	False, checkpoint_path, out_names,
                          	"save/restore_all", "save/Const:0",
                          	models_dir+model_filename, False, "")
#model = wide_resnet.WideResNet(image_size = 64,race = True, train_branch=False)()
#model.load_weights('weights/model_new.h5')
#model.save('weights/model.h5')
#model.summary()

output_names = ['kernel/gender_detection', 'kernel/age_detection', 'kernel/race']
convert_keras_to_pb('weights/model.h5', output_names,'weights', 'model_new.pb' )
frozen_graph_filename = 'weights/model_new.h5'
sess = K.get_session()

# freeze graph and remove training nodes
graph_def = tf.graph_util.convert_variables_to_constants(sess, sess.graph_def, output_names)
graph_def = tf.graph_util.remove_training_nodes(graph_def)

# write frozen graph to file
with open(frozen_graph_filename, 'wb') as f:
    f.write(graph_def.SerializeToString())
f.close()

# convert frozen graph to uff
uff_model = uff.from_tensorflow_frozen_model(frozen_graph_filename, output_names)





